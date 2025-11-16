from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from adk_app.symptom_agent import symptom_agent
from adk_app.appointment_agent import appointment_agent
from adk_app.insurance_agent import insurance_agent


class OrchestratorAgent(BaseAgent):
    """
    Module 3 Orchestrator:
    - Routes between Symptom Checker, Appointment Scheduler, and Insurance Verifier.
    - Stores light context in session.state for handoff.
    """
    name: str = "orchestrator"
    description: str = (
        "Routes queries to symptom checker, appointment scheduler, or insurance verifier, "
        "and maintains light session context."
    )

    async def _run_async_impl(
        self,
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        # Get the user message from the context
        user_msg = ""
        if hasattr(ctx, 'user_content') and ctx.user_content:
            if hasattr(ctx.user_content, 'parts') and ctx.user_content.parts:
                for part in ctx.user_content.parts:
                    if hasattr(part, 'text') and part.text:
                        user_msg = part.text
                        break
        
        msg_lower = user_msg.lower()
        state = ctx.session.state

        # Store the raw message for future context
        state["last_user_message"] = user_msg

        # --- Insurance intent: coverage / claims / benefits ---
        if any(
            kw in msg_lower
            for kw in [
                "insurance",
                "covered",
                "coverage",
                "claim",
                "copay",
                "co-pay",
                "deductible",
                "out of pocket",
            ]
        ):
            state["last_intent"] = "insurance"

            # Optionally pass last appointment or symptom info as hints
            # (The agent also sees chat history, but this can be structured.)
            reason = state.get("reason_for_visit") or state.get("last_user_message")
            state["insurance_reason"] = reason

            async for ev in insurance_agent.run_async(ctx):
                yield ev
            return

        # --- Appointment intent: schedule / book / reschedule ---
        if any(
            kw in msg_lower
            for kw in [
                "appointment",
                "schedule",
                "book a visit",
                "book an appointment",
                "reschedule",
            ]
        ):
            state["last_intent"] = "appointment"

            if "reason_for_visit" not in state:
                state["reason_for_visit"] = user_msg

            async for ev in appointment_agent.run_async(ctx):
                yield ev
            return

        # --- Default: Symptom checker ---
        state["last_intent"] = "symptom_check"
        async for ev in symptom_agent.run_async(ctx):
            yield ev


# Single root agent instance the FastAPI app uses
root_agent = OrchestratorAgent()
