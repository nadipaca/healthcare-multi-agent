from typing import Dict, List
import uuid
from datetime import datetime, timedelta

def list_active_prescriptions(patient_id: str) -> List[Dict]:
    """List patient's active prescriptions"""
    return [
        {
            "rx_id": "RX-001",
            "medication": "Lisinopril 10mg",
            "instructions": "Take 1 tablet daily",
            "refills_remaining": 2,
            "last_filled": (datetime.now() - timedelta(days=25)).isoformat(),
            "prescriber": "Dr. Smith",
        },
        {
            "rx_id": "RX-002",
            "medication": "Metformin 500mg",
            "instructions": "Take 1 tablet twice daily with meals",
            "refills_remaining": 0,
            "last_filled": (datetime.now() - timedelta(days=85)).isoformat(),
            "prescriber": "Dr. Johnson",
            "needs_renewal": True,
        }
    ]

def request_refill(rx_id: str, patient_id: str, pharmacy_id: str = "default") -> Dict:
    """Request prescription refill"""
    return {
        "refill_request_id": str(uuid.uuid4()),
        "rx_id": rx_id,
        "status": "SUBMITTED",
        "pharmacy": "Main Street Pharmacy",
        "estimated_ready": (datetime.now() + timedelta(days=1)).isoformat(),
        "message": "Refill request sent to pharmacy. You'll receive SMS when ready.",
    }