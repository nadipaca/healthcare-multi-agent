from typing import AsyncGenerator
from datetime import datetime

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from adk_app.symptom_agent import symptom_agent
from adk_app.appointment_agent import appointment_agent
from adk_app.insurance_agent import insurance_agent
from adk_app.feedback_agent import feedback_agent


class OrchestratorAgent(BaseAgent):
    """
    Module 4 Orchestrator:
    - Routes between Symptom Checker, Appointment Scheduler, Insurance Verifier, and Feedback Collector.
    - Stores light context in session.state for handoff between agents.
    - Enhanced orchestrator with better context management
    """
    name: str = "orchestrator"
    description: str = (
        "Routes queries to symptom checker, appointment scheduler, insurance verifier, "
        "or feedback collector, and maintains light session context."
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

        # Keep track of last raw message
        state["last_user_message"] = user_msg

         # Store conversation context
        state.setdefault("conversation_history", []).append({
            "message": user_msg,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Detect EMERGENCY keywords first (highest priority)
        emergency_keywords = [
            "chest pain", "can't breathe", "stroke", "suicide",
            "severe bleeding", "unconscious", "911"
        ]
        if any(kw in msg_lower for kw in emergency_keywords):
            state["last_intent"] = "emergency"
            state["severity"] = "critical"
            async for ev in emergency_agent.run_async(ctx):
                yield ev
            return
        
        # Medical records access
        if any(kw in msg_lower for kw in ["medical records", "my history", "past visits"]):
            state["last_intent"] = "medical_records"
            async for ev in medical_records_agent.run_async(ctx):
                yield ev
            return
        
        # Prescription management
        if any(kw in msg_lower for kw in ["prescription", "refill", "medication"]):
            state["last_intent"] = "prescription"
            async for ev in prescription_agent.run_async(ctx):
                yield ev
            return
        
        # Lab results
        if any(kw in msg_lower for kw in ["lab results", "test results", "blood work"]):
            state["last_intent"] = "lab_results"
            async for ev in lab_results_agent.run_async(ctx):
                yield ev
            return
        
        # Wellness/goals
        if any(kw in msg_lower for kw in ["health goal", "lose weight", "exercise plan"]):
            state["last_intent"] = "wellness"
            async for ev in wellness_agent.run_async(ctx):
                yield ev
            return

        # --- Feedback intent ---
        # Triggered when user explicitly says they want to give feedback / rate the system.
        if any(
            kw in msg_lower
            for kw in [
                "feedback",
                "rate this",
                "rate your help",
                "review this assistant",
                "complaint",
            ]
        ):
            state["last_intent"] = "feedback"
            async for ev in feedback_agent.run_async(ctx):
                yield ev
            return

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


# Root agent instance
root_agent = OrchestratorAgent()
