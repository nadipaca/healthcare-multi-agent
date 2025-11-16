# backend/adk_app/orchestrator_agent.py
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from .symptom_agent import symptom_agent


class OrchestratorAgent(BaseAgent):
    """
    For Module 1, this is just a thin wrapper:
    ALWAYS delegates to symptom_checker.
    Later modules will add real routing + other agents.
    """
    name: str = "orchestrator"
    description: str = "Routes queries to the symptom checker (Module 1)."

    async def _run_async_impl(
        self,
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        # Simply pass the context through to the symptom agent
        async for ev in symptom_agent.run_async(ctx):
            yield ev


# Export a single root agent instance for the app to use
root_agent = OrchestratorAgent()
