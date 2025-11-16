"""Test the orchestrator agent directly"""
import asyncio
from google.genai.types import Content, Part
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.invocation_context import InvocationContext
from adk_app.orchestrator_agent import root_agent

async def test_agent():
    print("Testing orchestrator agent...")
    
    # Create services
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    artifact_service = InMemoryArtifactService()
    
    # Create session
    app_name = "test-app"
    user_id = "test-user"
    session_id = "test-session"
    
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    session = await session_service.get_session(app_name, user_id, session_id)
    
    # Create message
    user_message = Content(
        role="user",
        parts=[Part(text="I need to schedule an appointment")]
    )
    
    print("Sending message: 'I need to schedule an appointment'")
    
    try:
        # Create context
        ctx = InvocationContext(
            session=session,
            user_id=user_id,
            new_message=user_message,
            session_service=session_service,
            memory_service=memory_service,
            artifact_service=artifact_service
        )
        
        # Run agent
        messages = []
        async for event in root_agent.run_async(ctx):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        messages.append(part.text)
                        print(f"Agent: {part.text}")
        
        print(f"\n✓ Success! Got {len(messages)} messages")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())
