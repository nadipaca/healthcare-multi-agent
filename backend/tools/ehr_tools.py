from typing import Dict, Any

# In real systems, this would call your FHIR MCP server / HTTP API.
# Here we keep responses mock and PHI-light.


def get_patient_summary(patient_id: str) -> Dict[str, Any]:
    """
    Mock FHIR lookup. Never returns full PHI in the LLM-visible layer.
    """
    # TODO: Replace with MPC/FHIR server call
    return {
        "patient_id": patient_id,
        "age": 34,
        "sex": "female",
        "known_conditions": ["hypertension"],
        "last_visit_summary": "Routine check-up, blood pressure mildly elevated.",
    }
