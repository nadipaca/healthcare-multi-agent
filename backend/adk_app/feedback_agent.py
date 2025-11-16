from google.adk.agents import Agent


feedback_agent = Agent(
    name="feedback_collector",
    model="gemini-2.5-flash-lite",
    description="Collects user feedback about the healthcare assistant.",
    instruction=(
        "You collect feedback from users about how helpful the assistant was.\n"
        "\n"
        "Behavior:\n"
        "- Ask the user for a rating from 1 to 5 (5 = extremely helpful).\n"
        "- Ask for 1–2 sentences of free-text feedback.\n"
        "- Summarize the main points in a short paragraph suitable for a human reviewer.\n"
        "- If the user mentions safety concerns, harm, or very negative experience "
        "(e.g. 'this advice hurt me', 'dangerous', 'malpractice'), then at the END of your response, "
        "add this line exactly:\n"
        "NEEDS_HUMAN_REVIEW: true\n"
        "- Otherwise, do not include that line.\n"
        "- Always thank the user for their feedback.\n"
    ),
    # Store feedback summary into session.state for future analytics, if needed.
    output_key="feedback_summary",
)
