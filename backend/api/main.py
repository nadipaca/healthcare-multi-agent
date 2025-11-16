# backend/api/main.py
import os
import uuid
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify API key is available
if not os.getenv("GOOGLE_API_KEY"):
    print("ERROR: GOOGLE_API_KEY not set in environment!")
    print("Please set it in your .env file or as an environment variable")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from google.genai.types import Content, Part
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.events import Event  # ADK event type

from api.models import ChatRequest, ChatResponse
from adk_app.orchestrator_agent import root_agent 

APP_NAME = "healthcare-multi-agent"
USER_ID = "demo_user"

app = FastAPI(title="Healthcare Symptom Checker (Module 1)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for local dev; tighten later for prod
    allow_credentials=True,
    allow_methods=["*"],
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


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    """
    Single-turn chat endpoint.

    - Creates/uses a session_id.
    - Sends user text to the ADK Runner.
    - Streams events and assembles text responses.
    - Detects 'NEEDS_HUMAN_REVIEW: true' marker for HITL.
    """
    session_id = payload.session_id or str(uuid.uuid4())

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

    return ChatResponse(
        session_id=session_id,
        messages=messages,
        needs_human_review=needs_human_review,
        agent_trace=dedup_trace,
    )
