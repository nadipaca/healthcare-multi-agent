from datetime import datetime, timedelta
from typing import List, Dict
import uuid


def list_open_slots_tool(
    specialty: str,
    after_datetime_iso: str,
    max_results: int,
) -> List[Dict]:
    """
    Return a list of available appointment slots.

    Args:
        specialty: e.g. "orthopedics", "primary care"
        after_datetime_iso: ISO 8601 string, e.g. "2025-11-20T17:00:00"
        max_results: how many slots to return

    Returns:
        A list of slot dicts. The agent will summarize these for the user.
    """
    start = datetime.fromisoformat(after_datetime_iso)

    slots: List[Dict] = []
    # Simple mock: every day, one slot at +1h after requested time
    for i in range(max_results):
        t = start + timedelta(days=i)
        slots.append(
            {
                "slot_id": str(uuid.uuid4()),
                "specialty": specialty,
                "start": t.isoformat(),
                "duration_minutes": 30,
                "location": "Main Clinic, 1st Floor",
            }
        )

    return slots


def book_appointment_tool(
    slot_id: str,
    patient_id: str,
    reason: str,
) -> Dict:
    """
    Book an appointment for the given slot and patient.

    Args:
        slot_id: ID from list_open_slots_tool
        patient_id: opaque patient identifier (no PHI)
        reason: short description of why they’re booking

    Returns:
        Booking confirmation dict.
    """
    return {
        "booking_id": str(uuid.uuid4()),
        "slot_id": slot_id,
        "patient_id": patient_id,
        "status": "BOOKED",
        "reason": reason,
        "message": "Mock appointment booked in scheduling system.",
    }
