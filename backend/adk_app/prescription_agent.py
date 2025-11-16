from google.adk.agents import Agent
from adk_app.tools.prescription_tools import (
    list_active_prescriptions,
    request_refill,
)

prescription_agent = Agent(
    name="prescription_manager",
    model="gemini-2.5-flash-lite",
    description="Manages prescription refills and medication information.",
    instruction=(
        "You help patients manage their prescriptions.\n"
        "- Use list_active_prescriptions() to show current medications\n"
        "- Highlight prescriptions needing renewal (refills_remaining = 0)\n"
        "- Help patients request refills using request_refill()\n"
        "- Confirm pharmacy details before submitting\n"
        "- Provide clear instructions on when/how to take medications\n"
        "- Never modify dosages or give medical advice about medications\n"
        "- For questions about side effects or interactions, recommend calling provider\n"
        "- Flag urgent issues (e.g., 'I missed 3 days of heart medication') for HITL\n"
    ),
    tools=[list_active_prescriptions, request_refill],
    output_key="prescription_summary",
)