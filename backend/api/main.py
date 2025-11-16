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
    Single-turn chat endpoint for Module 1 (symptom check + triage).

    - Creates/uses a session_id (so you can maintain state across turns).
    - Sends user text to the ADK Runner as Content/Part.
    - Streams all events and collects the final text response.
    """
    try:
        session_id = payload.session_id or str(uuid.uuid4())

        # Ensure there is a session for this conversation
        await ensure_session(session_id)

        runner = get_runner()

        # Wrap plain user text into ADK Content/Part
        user_message: Content = Content(
            role="user",
            parts=[Part(text=payload.message)],
        )

        # Collect all text segments from the event stream
        messages: List[str] = []

        # ADK's async streaming API
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=user_message,
        ):
            # Event is google.adk.events.Event
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        messages.append(part.text)

        # Optionally, you can join or just return the list
        # Here: we return all segments to keep frontend flexible
        return ChatResponse(session_id=session_id, messages=messages)
    
    except Exception as e:
        import traceback
        print(f"Error in chat endpoint: {e}")
        print(traceback.format_exc())
        raise
