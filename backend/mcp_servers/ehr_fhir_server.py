from fastmcp import FastMCP
from typing import Dict, Any

mcp = FastMCP("EHR-FHIR-Server")


@mcp.tool
def get_patient_demographics(patient_id: str) -> Dict[str, Any]:
    """Return non-sensitive demographics for a patient."""
    # Mock only, no real PHI
    return {
        "patient_id": patient_id,
        "age": 34,
        "sex": "female",
    }


@mcp.tool
def get_recent_encounters(patient_id: str, limit: int = 3):
    """Return a limited list of recent encounters with scrubbed text."""
    return [
        {"date": "2025-11-01", "summary": "Routine follow-up; BP mildly elevated."},
        {"date": "2025-09-10", "summary": "Annual physical; labs ordered."},
    ][:limit]


if __name__ == "__main__":
    # stdio for local dev; can also use HTTP transport.
    mcp.run()
