from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from adk_app.symptom_agent import symptom_agent
from adk_app.appointment_agent import appointment_agent


class OrchestratorAgent(BaseAgent):
    """
    Module 2 Orchestrator:
    - Routes between Symptom Checker and Appointment Scheduler.
    - Stores light context in session.state for handoff.
    """
    name: str = "orchestrator"
    description: str = (
        "Routes queries to symptom checker or appointment scheduler, "
        "and maintains light session context."
    )

    async def _run_async_impl(
        self,
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        # Get the user message from the context
        user_msg = ""
        
        # Check user_content attribute (this is what ADK uses)
        if hasattr(ctx, 'user_content') and ctx.user_content:
            # user_content is a Content object with parts
            if hasattr(ctx.user_content, 'parts') and ctx.user_content.parts:
                for part in ctx.user_content.parts:
                    if hasattr(part, 'text') and part.text:
                        user_msg = part.text
                        break
        
        msg_lower = user_msg.lower()

        # basic state access
        state = ctx.session.state
        state["last_user_message"] = user_msg

        # --- Routing logic ---
        if any(word in msg_lower for word in ["appointment", "schedule", "book a visit", "book an appointment"]):
            state["last_intent"] = "appointment"

            # Optionally, carry last symptom summary into state["reason_for_visit"]
            # For now, we simply reuse the last user message as the reason.
            if "reason_for_visit" not in state:
                state["reason_for_visit"] = user_msg

            async for ev in appointment_agent.run_async(ctx):
                yield ev

        else:
            state["last_intent"] = "symptom_check"
            async for ev in symptom_agent.run_async(ctx):
                yield ev


# Single root agent that FastAPI's Runner will use
root_agent = OrchestratorAgent()
