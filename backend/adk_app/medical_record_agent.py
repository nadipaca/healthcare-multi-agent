from google.adk.agents import Agent
from adk_app.tools.ehr_tools import get_patient_summary

medical_records_agent = Agent(
    name="medical_records_viewer",
    model="gemini-2.5-flash-lite",
    description="Retrieves and summarizes patient medical history securely.",
    instruction=(
        "You help patients view their medical records and history.\n"
        "- ALWAYS verify you're speaking to the authorized patient\n"
        "- Use get_patient_summary() to fetch records\n"
        "- Summarize in plain language, explaining medical terms\n"
        "- Never share full PHI in responses - use abstractions\n"
        "- Highlight important items: allergies, chronic conditions, recent visits\n"
        "- If asked about specific test results, explain what they mean in context\n"
        "- Remind users this is for informational purposes only\n"
        "- For detailed questions, recommend consulting their provider\n"
    ),
    tools=[get_patient_summary],
    output_key="medical_history_summary",
)