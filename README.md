## Healthcare Multi‑Agent Assistant

End‑to‑end demo of a healthcare‑focused multi‑agent system that helps patients with symptom triage, appointment scheduling, insurance questions, and feedback collection, while keeping safety and human‑in‑the‑loop (HITL) controls at the center.

---

## 1. Problem & Value

Modern healthcare systems are fragmented for patients:
- Symptom advice is generic and disconnected from their records.
- Booking the right specialist is confusing.
- Insurance coverage is hard to understand.
- Feedback rarely flows back into system improvements.

This project shows how **agents** can coordinate across these touchpoints to provide:
- Safer, more contextual symptom guidance.
- Smart routing to the right specialist and time slot.
- Clear explanations of insurance coverage and out‑of‑pocket estimates.
- Continuous feedback signals for quality and analytics.

> All medical content is **informational only** and is **not** a diagnosis or medical advice. Users should always consult a clinician for care decisions.

---

## 📹 Video Tutorial

[▶️ Watch the demo video](./docs/assets/demo.mp4)

## 2. Core User Stories & Agent Roles

### 2.1 Symptom Check & Triage
- Actor: Patient  
- Flow:
  - User: “I have a headache and blurred vision.”  
  - **Orchestrator Agent** classifies intent = `symptom_check`.  
  - **Symptom Agent**:
    - Asks focused follow‑up questions (onset, severity, red flags).
    - Uses medical reference / lab context via tools.
    - Produces structured triage: `severity`, `recommended_next_step`, `red_flags_detected`.
  - For high‑risk patterns (e.g. stroke, chest pain) the orchestrator flags **NEEDS_HUMAN_REVIEW** and strongly advises urgent care.
  - **Feedback Agent** can later collect a rating on how helpful this was.

### 2.2 Appointment & Contextual Handoff
- Actor: Patient  
- Flow:
  - User: “Book an appointment for my knee pain next week after 5pm.”  
  - **Orchestrator** uses session state (symptom summary, severity, demographics) and routes to **Appointment Agent**.
  - **Appointment Agent**:
    - Calls scheduling tools / mock EHR (MCP‑style) to list open slots.
    - Chooses an appropriate specialty (e.g. orthopedics vs primary care).
    - Books the chosen slot, saves to DB, and returns a structured appointment summary.
  - The appointment details and prior symptom summary are stored so downstream agents can see the context.

### 2.3 Insurance Verification & Claims
- Actor: Patient  
- Flow:
  - User: “Will my MRI tomorrow be covered?”  
  - **Orchestrator + Insurance Agent** handle the query.
  - **Insurance Agent**:
    - Calls mock insurance tools (e.g. `check_eligibility`, `estimate_copay`) with plan / provider details.
    - Explains coverage, likely copay, and caveats in plain language.
    - If key data is missing, asks for minimal extra info or suggests contacting the insurer.

### 2.4 Feedback & Quality Loop
- Actor: Patient or clinician  
- Flow:
  - After major interactions, **Feedback Agent** prompts for a short rating + comments.
  - Feedback is stored in an audit‑friendly log and contributes to analytics and agent evaluation.

---

## 3. Architecture Overview

**High‑level components**
- **Frontend** (`frontend/`): Simple UI for chat + patient context (not deeply covered here).
- **Backend API** (`backend/api/main.py`):
  - FastAPI app exposing `/api/chat`, health, analytics, and patient routes.
  - Uses **ADK `Runner`** to orchestrate agent sessions.
  - Integrates rate limiting, analytics, chat history storage, and file‑based lab/prescription OCR context.
- **Agents** (`backend/adk_app/`):
  - `orchestrator_agent.py`: root agent coordinating sub‑agents and tools.
  - `symptom_agent.py`: symptom triage with safety rules.
  - `appointment_agent.py`: context‑aware scheduling using tools.
  - `insurance_agent.py`: coverage and cost explanation.
  - `feedback_agent.py`, `emergency_agent.py`, `wellness_agent.py`, etc. for vertical tasks.
- **Tools / MCP‑style integrations** (`backend/adk_app/tools/`):
  - `scheduling_tools.py`: list and book appointment slots.
  - `insurance_tools.py`: mock eligibility and copay estimation.
  - `lab_results_tools.py`, `prescription_refill_tools.py`, `ehr_tools.py` for deeper clinical context.
  - `smart_routing.py`: shared logic to map symptoms + history → specialty + urgency.
- **Database Layer** (`backend/database/`):
  - `healthcare.db` SQLite database.
  - `db_helper.py` for patients, appointments, prescriptions, labs, insurance, chat history, files, and feedback.
- **Analytics & Safety**:
  - `api/rate_limiter.py`: per‑session request limits.
  - `api/analytics.py` + `dashboard.html`: metrics, HITL flags, response times, ratings.
  - HITL signal via `NEEDS_HUMAN_REVIEW: true` in agent outputs.

**Key agent concepts demonstrated**
- Multi‑agent orchestration (orchestrator + specialist agents).
- Tool calling for structured backends (scheduling, insurance, labs, EHR).
- Session + memory: state carried across turns via ADK Runner and DB.
- Safety rules & escalation paths for high‑risk medical content.

---

## 4. Implementation & Technology

- **Language / Frameworks**
  - Python, FastAPI backend (`backend/api`).
  - ADK (`google.adk`) for agents, sessions, memory, and artifacts.
  - SQLite for persistence (`backend/database/healthcare.db`).
- **Models**
  - `gemini-2.5-flash-lite` for sub‑agents (symptoms, appointments, insurance, etc.).
  - `gpt-4o-mini` (via `LiteLlm`) for the root orchestrator agent.
- **Testing**
  - `backend/tests/` contains example tests, scripts, and a testing guide:
    - API and agent behavior tests.
    - Rate limiter and analytics test scripts.
  - See `backend/tests/TESTING_GUIDE.md` and `backend/tests/SUMMARY.md` for more.

---

## 5. Setup & Running Locally

### 5.1 Prerequisites
- Python 3.10+  
- Node.js (if you want to run the frontend)  
- A valid `OPENAI_API_KEY` (for the LiteLlm wrapper) and access to Gemini models (configured via ADK / environment).

### 5.2 Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
