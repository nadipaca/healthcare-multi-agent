from google.adk.agents import Agent

from adk_app.tools.insurance_tools import (
    check_eligibility_tool,
    estimate_copay_tool,
)


insurance_agent = Agent(
    name="insurance_verifier",
    model="gemini-2.5-flash-lite",
    description="Explains mock insurance coverage, eligibility, and cost estimates.",
    instruction=(
        "You help patients understand whether a procedure is likely to be covered "
        "by their insurance and what they might pay.\n"
        "\n"
        "Guidelines:\n"
        "- ALWAYS clarify you are giving general information, not financial or legal advice.\n"
        "- Start by confirming key details (member ID or plan type, procedure, provider in/out-of-network).\n"
        "- Use check_eligibility_tool(...) to fetch high-level coverage info.\n"
        "- Use estimate_copay_tool(...) to estimate patient responsibility.\n"
        "- If any key data is missing, ask concise follow-up questions.\n"
        "- If the user does not want to provide details, tell them to call their insurer.\n"
        "- Clearly mark all numbers as 'estimates' and not guarantees.\n"
        "- Use plain language; avoid raw codes unless the user asks.\n"
        "- If the session contains an upcoming appointment summary or reason-for-visit,\n"
        "  consider that when explaining coverage.\n"
        "- End with a short bullet list: what is covered, what might not be, and what the user should do next.\n"
    ),
    tools=[check_eligibility_tool, estimate_copay_tool],
    output_key="insurance_summary",  # stored in session.state for downstream agents
)
