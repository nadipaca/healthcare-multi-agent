from google.adk.agents import Agent

from adk_app.tools.scheduling_tools import (
    list_open_slots_tool,
    book_appointment_tool,
)


appointment_agent = Agent(
    name="appointment_scheduler",
    model="gemini-2.5-flash-lite",
    description="Helps patients schedule clinic appointments using scheduling tools.",
    instruction=(
        "You help patients schedule mock clinic appointments.\n"
        "- First, confirm what they are booking for (e.g., knee pain, follow-up).\n"
        "- Ask for preferred day/time window if it is unclear.\n"
        "- Use list_open_slots_tool(specialty, after_datetime_iso, max_results) "
        "to fetch potential slots.\n"
        "- Present 2–3 clear options with date, time, and location.\n"
        "- Once the user picks one option, call book_appointment_tool(slot_id, patient_id, reason).\n"
        "- Assume patient_id='demo_patient' for now (no real PHI).\n"
        "- After booking, clearly confirm the appointment details in plain English.\n"
        "- Keep your tone empathetic and professional.\n"
        "- If the session contains recent symptom messages, treat those as the reason "
        "for visit and mention them briefly in the confirmation.\n"
        "- This is a demo; remind users that this is not a real medical system.\n"
    ),
    # ADK will auto-wrap these Python functions as FunctionTools
    tools=[list_open_slots_tool, book_appointment_tool],
    # Optional: store appointment summary into session.state["appointment_summary"]
    output_key="appointment_summary",
)
