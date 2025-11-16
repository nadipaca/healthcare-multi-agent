# backend/api/main.py
import os
import uuid
import time
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify API key is available
if not os.getenv("GOOGLE_API_KEY"):
    print("ERROR: GOOGLE_API_KEY not set in environment!")
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

APP_NAME = "healthcare-multi-agent"
USER_ID = "demo_user"

app = FastAPI(title="Healthcare Symptom Checker (Module 1)")

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
    session_id = payload.session_id or str(uuid.uuid4())
    
    # Apply rate limiting
    await rate_limiter.check_rate_limit(session_id)
    
    # Start timing for analytics
    start_time = time.time()

    # Ensure session exists
    await ensure_session(session_id)

    runner = get_runner()

    # Wrap user text
    user_message: Content = Content(
        role="user",
        parts=[Part(text=payload.message)],
    )

    messages: List[str] = []
    needs_human_review = False
    agent_trace: List[str] = []

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
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
