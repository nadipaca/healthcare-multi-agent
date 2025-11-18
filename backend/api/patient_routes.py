from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import db_helper

router = APIRouter(prefix="/api/patient", tags=["patient"])

class PatientAuthRequest(BaseModel):
    auth_method: Literal["email", "phone", "patient_id"]
    identifier: str

class NewPatientRegistration(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    insurance_id: Optional[str] = None

@router.post("/authenticate")
async def authenticate_patient(request: PatientAuthRequest):
    try:
        patient = None
        if request.auth_method == "email":
            patient = db_helper.get_patient_by_email(request.identifier)
        elif request.auth_method == "phone":
            patient = db_helper.get_patient_by_phone(request.identifier)
        elif request.auth_method == "patient_id":
            patient = db_helper.get_patient_by_id(request.identifier)
        
        if patient:
            full_data = {
                "patient": patient,
                "prescriptions": db_helper.get_patient_prescriptions(patient['patient_id']),
                "appointments": db_helper.get_patient_appointments(patient['patient_id']),
                "insurance": db_helper.get_patient_insurance(patient['patient_id']),
                "medical_history": db_helper.get_medical_history(patient['patient_id']),
                "lab_results": db_helper.get_lab_results(patient['patient_id'])
            }
            return {"status": "success", "patient": patient, "full_data": full_data, "message": f"Welcome back, {patient['first_name']}!"}
        else:
            return {"status": "new_patient", "message": "We don't have a record for you.", "identifier": request.identifier, "auth_method": request.auth_method}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register")
async def register_new_patient(patient_data: NewPatientRegistration):
    try:
        new_patient_id = db_helper.generate_patient_id()
        patient = db_helper.create_patient(patient_id=new_patient_id, first_name=patient_data.first_name, last_name=patient_data.last_name, date_of_birth=patient_data.date_of_birth, email=patient_data.email, phone=patient_data.phone, address=patient_data.address, insurance_id=patient_data.insurance_id, medical_history="")
        return {"status": "success", "patient": patient, "message": f"Welcome, {patient_data.first_name}!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update/{patient_id}")
async def update_patient_record(patient_id: str, updates: dict):
    try:
        updated_patient = db_helper.update_patient_record(patient_id, updates)
        return {"status": "success", "patient": updated_patient, "message": "Medical record updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/{patient_id}")
async def get_patient_full_data(patient_id: str):
    try:
        patient = db_helper.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        full_data = {"patient": patient, "prescriptions": db_helper.get_patient_prescriptions(patient_id), "appointments": db_helper.get_patient_appointments(patient_id), "insurance": db_helper.get_patient_insurance(patient_id), "medical_history": db_helper.get_medical_history(patient_id), "lab_results": db_helper.get_lab_results(patient_id)}
        return {"status": "success", "data": full_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
