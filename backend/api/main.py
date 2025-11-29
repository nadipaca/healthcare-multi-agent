# backend/api/main.py
import os
import uuid
import time
from typing import List, Optional
from dotenv import load_dotenv
from database import db_helper

# Load environment variables
load_dotenv()

# Verify API key is available
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set in environment!")
    print("Please set it in your .env file or as an environment variable")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from google.genai.types import Content, Part
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.events import Event  # ADK event type

from api.models import ChatRequest, ChatResponse
from adk_app.orchestrator_agent import root_agent
from api.rate_limiter import rate_limiter
from api.analytics import analytics
from database import db_helper
from api.testing_routes import router as testing_router
from api.patient_routes import router as patient_router
from api.chat_history_routes import router as chat_history_router
from api.gcp_ocr import extract_text_from_file

APP_NAME = "agents"
USER_ID = "demo_user"

app = FastAPI(title="Healthcare Multi-Agent System")

# Include testing routes
app.include_router(testing_router)
app.include_router(patient_router)
app.include_router(chat_history_router)

# CORS configuration - more explicit for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- Runner + services singletons for this process ---

_session_service: Optional[InMemorySessionService] = None
_memory_service: Optional[InMemoryMemoryService] = None
_artifact_service: Optional[InMemoryArtifactService] = None
_runner: Optional[Runner] = None


def get_runner() -> Runner:
    """
    Lazily create a Runner wired to our root_agent.

    This uses in-memory session + memory + artifacts, which is perfect
    for local Module 1 development. In later modules we can swap these
    for DB/Vertex-based services without changing the FastAPI routes.
    """
    global _runner, _session_service, _memory_service, _artifact_service

    if _runner is None:
        _session_service = InMemorySessionService()
        _memory_service = InMemoryMemoryService()
        _artifact_service = InMemoryArtifactService()

        _runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=_session_service,
            memory_service=_memory_service,
            artifact_service=_artifact_service,
        )

    return _runner


async def ensure_session(session_id: str):
    """
    Make sure a session exists for (APP_NAME, USER_ID, session_id).
    If it doesn't, create one.

    This is the canonical pattern from ADK docs for sessionful agents.
    """
    runner = get_runner()
    session_service = runner.session_service

    # Newer ADK sessions API is async
    existing = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    if existing is None:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
        )


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "healthcare-multi-agent"}


@app.options("/api/chat")
async def chat_options():
    """Handle CORS preflight requests for the chat endpoint"""
    return {}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: Request, payload: ChatRequest):
    """
    Single-turn chat endpoint with rate limiting and analytics.

    - Creates/uses a session_id.
    - Applies rate limiting per session
    - Tracks analytics metrics
    - Sends user text to the ADK Runner.
    - Streams events and assembles text responses.
    - Detects 'NEEDS_HUMAN_REVIEW: true' marker for HITL.
    """
    patient_id = payload.patient_id
    file_ids = payload.file_ids or []
    session_id = payload.session_id

    # Align chat session ID with database chat session when a patient is known
    if patient_id:
        try:
            # This will return an existing active session for the patient
            # or create a new one if needed.
            canonical_session_id = db_helper.get_or_create_session(patient_id, session_id)
            session_id = canonical_session_id
        except Exception:
            import traceback
            traceback.print_exc()
            # Fallback to a random session if DB lookup fails
            session_id = session_id or str(uuid.uuid4())

        # Persist the incoming user message against the DB chat session
        try:
            db_helper.save_chat_message(session_id=session_id, role='user', content=payload.message)
        except Exception:
            import traceback
            traceback.print_exc()
    else:
        # No patient context – use provided session_id or generate a new one
        session_id = session_id or str(uuid.uuid4())

    # Apply rate limiting using the final session_id
    await rate_limiter.check_rate_limit(session_id)

    # Start timing for analytics
    start_time = time.time()

    # Ensure an ADK session exists for this (app, user, session_id)
    await ensure_session(session_id)

    runner = get_runner()

    lab_context = ""
    if patient_id and any(kw in payload.message.lower() for kw in ["lab", "test result", "blood work"]):
        lab_lines = []

        # 1) Structured lab results from lab_results table
        structured_labs = db_helper.get_lab_results(patient_id)[:3]  # last 3
        for lab in structured_labs:
            lab_lines.append(
                f"{lab['test_date']}: {lab['test_name']} = {lab['result_value']} {lab['unit']} (ref: {lab['reference_range']})"
            )

        # 2) Fallback to recent uploaded lab-result documents (if no structured labs)
        if not lab_lines:
            try:
                recent_lab_docs = db_helper.get_patient_files(patient_id, "lab_result")[:2]
                for doc in recent_lab_docs:
                    extracted = doc.get("extracted_text") or ""
                    if extracted:
                        # Truncate to avoid overloading context
                        snippet = extracted[:800]
                        lab_lines.append(
                            f"Lab document: {doc.get('file_name', 'unknown')}\n{snippet}"
                        )
            except Exception:
                # If anything goes wrong fetching documents, just skip the fallback
                pass

        if lab_lines:
            lab_context = "Recent lab results for this patient:\n" + "\n".join(lab_lines) + "\n\n"

    # Add context from prescription documents when the user asks about medications
    rx_context = ""
    if patient_id and any(
        kw in payload.message.lower()
        for kw in ["prescription", "prescriptions", "medication", "medications", "meds", "drug", "drugs"]
    ):
        rx_lines: List[str] = []

        # 1) Structured prescription records
        try:
            structured_rx = db_helper.get_patient_prescriptions(patient_id)[:5]
            for rx in structured_rx:
                med = rx.get("medication") or "Unknown medication"
                dose = rx.get("dosage") or ""
                instructions = rx.get("instructions") or ""
                indication = rx.get("indication") or ""
                last_filled = rx.get("last_filled") or "unknown date"
                refills = rx.get("refills_remaining")
                refills_str = f", refills remaining: {refills}" if refills is not None else ""

                detail_parts = [p for p in [instructions, indication] if p]
                details = " - ".join(detail_parts) if detail_parts else ""

                line = f"{med} {dose}".strip()
                if details:
                    line += f": {details}"
                line += f" (last filled {last_filled}{refills_str})"
                rx_lines.append(line)
        except Exception:
            import traceback
            traceback.print_exc()

        # 2) Recent uploaded prescription documents with OCR text (from medical_documents)
        try:
            recent_rx_docs = db_helper.get_patient_files(patient_id, "prescription")[:3]
            for doc in recent_rx_docs:
                extracted = doc.get("extracted_text") or ""
                if extracted:
                    snippet = extracted[:800]
                    rx_lines.append(
                        f"Prescription document: {doc.get('file_name', 'unknown')}\n{snippet}"
                    )
        except Exception:
            import traceback
            traceback.print_exc()

        # 3) Backfill from prescription_files if older uploads were not mirrored into medical_documents
        try:
            if not rx_lines:
                rx_files = db_helper.get_prescription_files(patient_id)[:3]
                for pf in rx_files:
                    snippet = ""
                    try:
                        snippet = extract_text_from_file(pf["file_path"], pf.get("file_type"))
                    except Exception:
                        import traceback
                        traceback.print_exc()

                    if snippet:
                        text_snippet = snippet[:800]
                        rx_lines.append(
                            f"Prescription document: {pf.get('file_name', 'unknown')}\n{text_snippet}"
                        )
                        # Persist into medical_documents so future calls don't need to re-OCR
                        try:
                            db_helper.save_prescription_document_file(
                                patient_id=patient_id,
                                file_name=pf.get("file_name", ""),
                                file_path=pf.get("file_path", ""),
                                file_type=pf.get("file_type", ""),
                                file_size=pf.get("file_size", 0),
                                notes=pf.get("notes"),
                                extracted_text=text_snippet,
                                gcs_uri=pf.get("gcs_uri"),
                            )
                        except Exception:
                            import traceback
                            traceback.print_exc()
        except Exception:
            import traceback
            traceback.print_exc()

        if rx_lines:
            rx_context = "Current prescription information for this patient:\n" + "\n".join(rx_lines) + "\n\n"
        else:
            # Explicitly tell the model that we checked and found no prescriptions,
            # so it doesn't assume it lacks access.
            rx_context = (
                "Current prescription information for this patient:\n"
                "- There are no active prescriptions on file in the system.\n\n"
            )


    # existing ocr_context from medical_documents
    ocr_context = ""
    if file_ids:
        for fid in file_ids:
            doc = db_helper.get_file_by_id(fid)
            if doc and doc.get("extracted_text"):
                ocr_context += f"\n--- File: {doc.get('file_name')} ---\n{doc['extracted_text']}\n"

    context = lab_context + rx_context + ocr_context
    full_message = f"{context}User message: {payload.message}" if context else payload.message

    # ...use full_message in agent invocation...
    user_message: Content = Content(
        role="user",
        parts=[Part(text=full_message)],
    )

    messages: List[str] = []
    needs_human_review = False
    agent_trace: List[str] = []

    async for event in runner.run_async(
        session_id=session_id,
        user_id=USER_ID,
        new_message=user_message,
    ):
        # Collect text from events
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    text = part.text
                    messages.append(text)

                    # If the agent used the special flag, mark for human review
                    if "NEEDS_HUMAN_REVIEW: true" in text:
                        needs_human_review = True

        # If event has agent_name (depending on ADK version), capture it.
        # We'll guard with getattr to avoid crashes if the attr doesn't exist.
        agent_name = getattr(event, "agent_name", None)
        if agent_name:
            agent_trace.append(agent_name)

    # Deduplicate agent_trace while preserving order
    seen = set()
    dedup_trace: List[str] = []
    for name in agent_trace:
        if name not in seen:
            seen.add(name)
            dedup_trace.append(name)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Record analytics
    primary_agent = dedup_trace[0] if dedup_trace else "unknown"
    total_response_length = sum(len(msg) for msg in messages)
    
    analytics.record_interaction(
        session_id=session_id,
        agent_name=primary_agent,
        user_message=payload.message,
        response_length=total_response_length,
        duration_ms=duration_ms,
        hitl_flagged=needs_human_review,
    )

    try:
        for msg in messages:
            db_helper.save_chat_message(
                session_id=session_id,
                role='assistant',
                content=msg,
                agent_name=primary_agent,
                needs_human_review=needs_human_review
            )
    except Exception:
        import traceback
        traceback.print_exc()

    return ChatResponse(
        session_id=session_id,
        messages=messages,
        needs_human_review=needs_human_review,
        agent_trace=dedup_trace,
    )


# ========== Analytics & Monitoring Endpoints ==========

@app.get("/api/analytics/dashboard")
async def get_dashboard_metrics(hours: int = 24):
    """
    Get comprehensive dashboard metrics.
    
    Args:
        hours: Number of hours to look back (default 24)
        
    Returns:
        Dashboard metrics including agent usage, performance, and HITL flags
    """
    return analytics.get_dashboard_metrics(hours=hours)


@app.get("/api/analytics/session/{session_id}")
async def get_session_analytics(session_id: str):
    """
    Get detailed analytics for a specific session.
    
    Args:
        session_id: The session ID to retrieve
        
    Returns:
        Detailed session metrics or 404 if not found
    """
    from fastapi import HTTPException
    
    session_data = analytics.get_session_details(session_id)
    if session_data is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_data


@app.get("/api/analytics/rate-limits/{session_id}")
async def get_rate_limits(session_id: str):
    """
    Get remaining rate limits for a session.
    
    Args:
        session_id: The session ID to check
        
    Returns:
        Remaining requests per minute and per hour
    """
    return await rate_limiter.get_remaining_requests(session_id)


@app.post("/api/feedback/rating")
async def submit_rating(session_id: str, agent_name: str, rating: int):
    """
    Submit a user rating for an agent interaction.
    
    Args:
        session_id: Session ID
        agent_name: Name of the agent being rated
        rating: Rating from 1-5
        
    Returns:
        Confirmation message
    """
    from fastapi import HTTPException
    
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    analytics.record_rating(session_id, agent_name, rating)
    
    return {
        "status": "success",
        "message": "Rating recorded",
        "session_id": session_id,
        "rating": rating
    }
