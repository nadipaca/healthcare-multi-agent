1. Core user stories & agent roles

- User Story 1 – Symptom Check & Triage

  - Actor: Patient

  - Flow:

    - User: “I have a headache and blurred vision.”

    - Orchestrator Agent classifies intent = symptom_check.

    - Symptom Checker Agent:
      - Asks a few follow-up questions.
      - Uses Medical Reference Agent + MCP FHIR server to ground advice.
      - Produces structured triage: severity, recommended_next_step, red_flags_detected.

    - If high-risk (e.g., chest pain, stroke signs), Orchestrator flags HITL review and explicitly advises urgent professional care.

    - Feedback Agent logs how helpful this was.

    - All medical output must be explicitly “not a diagnosis, informational only, see a clinician.”

- User Story 2 – Appointment & Contextual Handoff

  - Actor: Patient

  - Flow:

    - User: “Book an appointment for my knee pain next week after 5pm.”

    - Orchestrator:
      - Uses session state: last symptoms, demographics.
      - Routes to Appointment/Scheduling Agent.

    - Appointment Agent:
      - Calls Scheduling MCP server (mock EHR scheduling API) for open slots.
      - Suggests options, books appointment.
      - Appointment details and previous symptom summary are written to session + long-term memory so future agents see the context.

- User Story 3 – Insurance Verification & Claims

  - Actor: Patient

  - Flow:

    - User: “Will my MRI tomorrow be covered?”

    - Orchestrator → Insurance Verifier Agent.

    - Insurance Verifier:
      - Calls Insurance MCP server lookup_claim_eligibility with plan ID, CPT code, provider, etc.
      - Summarizes benefits, co-pay estimates, caveats.
      - If data missing → asks for consent to pull more details, or instructs user to call insurer.

- User Story 4 – Feedback & Quality

  - Actor: Patient or clinician

  - Flow:

    - After major interactions, Orchestrator → Feedback Collector Agent.
      - Captures ratings + free-text.
      - Stores in audit-safe log for evaluation metrics.