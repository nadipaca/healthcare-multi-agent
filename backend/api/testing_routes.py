"""
Testing endpoints for healthcare multi-agent system
Allows frontend to select patient and test all agents
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add parent directory to path to import database module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import db_helper

router = APIRouter(prefix="/api/testing", tags=["testing"])

class PatientSelection(BaseModel):
    patient_id: str

class TestDataResponse(BaseModel):
    patient: dict
    prescriptions: List[dict]
    appointments: List[dict]
    insurance: Optional[dict]
    medical_history: List[dict]
    lab_results: List[dict]

@router.get("/patients")
async def get_all_test_patients():
    """Get all sample patients for testing"""
    try:
        patients = db_helper.get_all_patients()
        return {
            "status": "success",
            "patients": patients,
            "message": f"Found {len(patients)} test patients"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{patient_id}")
async def get_patient_test_data(patient_id: str):
    """Get all data for a specific patient"""
    try:
        patient = db_helper.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        prescriptions = db_helper.get_patient_prescriptions(patient_id)
        appointments = db_helper.get_patient_appointments(patient_id)
        insurance = db_helper.get_patient_insurance(patient_id)
        medical_history = db_helper.get_medical_history(patient_id)
        lab_results = db_helper.get_lab_results(patient_id)
        
        return {
            "status": "success",
            "data": {
                "patient": patient,
                "prescriptions": prescriptions,
                "appointments": appointments,
                "insurance": insurance,
                "medical_history": medical_history,
                "lab_results": lab_results
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/select-patient")
async def select_test_patient(selection: PatientSelection):
    """
    Select a patient for testing session
    This stores the patient_id in the session for the agents to use
    """
    try:
        patient = db_helper.get_patient_by_id(selection.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return {
            "status": "success",
            "patient": patient,
            "message": f"Now testing as {patient['first_name']} {patient['last_name']}",
            "session_context": {
                "patient_id": patient['patient_id'],
                "patient_name": f"{patient['first_name']} {patient['last_name']}",
                "has_insurance": patient['insurance_id'] is not None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenarios")
async def get_test_scenarios():
    """Get predefined test scenarios for each agent"""
    return {
        "status": "success",
        "scenarios": [
            {
                "agent": "symptom_checker",
                "patient": "PAT001 - John Doe",
                "scenario": "Patient with hypertension experiencing headache",
                "test_message": "I have a bad headache and feel dizzy",
                "expected_flow": "Symptom assessment → Appointment suggestion → Insurance check"
            },
            {
                "agent": "prescription_manager",
                "patient": "PAT001 - John Doe",
                "scenario": "Patient needs refill for Metformin (0 refills remaining)",
                "test_message": "I need a refill for my diabetes medication",
                "expected_flow": "List prescriptions → Identify need for renewal → Contact provider"
            },
            {
                "agent": "appointment_scheduler",
                "patient": "PAT002 - Jane Smith",
                "scenario": "Patient with migraine history wants appointment",
                "test_message": "I need to see a doctor about my migraines",
                "expected_flow": "Check history → Suggest neurology → Book appointment"
            },
            {
                "agent": "insurance_verifier",
                "patient": "PAT003 - Mike Johnson",
                "scenario": "Check coverage for orthopedics visit",
                "test_message": "Will my insurance cover orthopedics?",
                "expected_flow": "Check eligibility → Show copay → Explain coverage"
            },
            {
                "agent": "feedback_collector",
                "patient": "Any patient",
                "scenario": "Collect experience feedback",
                "test_message": "I want to give feedback about my visit",
                "expected_flow": "Collect rating → Get comments → Save feedback"
            }
        ]
    }
