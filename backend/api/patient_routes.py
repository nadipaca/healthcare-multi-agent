from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal, List
import sys
import os
import re
import uuid
from datetime import datetime
from api.gcp_ocr import extract_text_from_file

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import db_helper
from api.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    get_current_user,
    require_patient
)
from api.file_handler import save_uploaded_file, validate_file
from api.config import settings

router = APIRouter(prefix="/api/patient", tags=["patient"])
auth_scheme = HTTPBearer()

# ============= Authentication Models =============

class PatientAuthRequest(BaseModel):
    auth_method: Literal["email", "phone", "patient_id"]
    identifier: str
    password: Optional[str] = None  # For email authentication

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class NewPatientRegistration(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None
    insurance_id: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    patient: dict

class FileUploadResponse(BaseModel):
    file_id: str
    file_name: str
    file_type: str
    uploaded_at: str
    message: str

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Optional: Check for special characters
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     return False, "Password must contain at least one special character"
    
    return True, ""

# ============= Authentication Endpoints =============

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate patient with email and password
    Returns JWT tokens
    """
    try:
        # Get patient by email
        patient = db_helper.get_patient_by_email(credentials.email)
        
        if not patient:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Check if password_hash exists (for backward compatibility)
        password_hash = patient.get('password_hash')
        if not password_hash:
            # If no password hash, create one with the provided password
            # This is for existing patients without passwords
            password_hash = hash_password(credentials.password)
            db_helper.update_patient_record(patient['patient_id'], {
                'password_hash': password_hash
            })
        
        # Verify password
        if not verify_password(credentials.password, password_hash):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Check if account is active (default to True if field doesn't exist)
        is_active = patient.get('is_active', True)
        if not is_active:
            raise HTTPException(
                status_code=403,
                detail="Account is deactivated. Please contact support."
            )
        
        # Create tokens
        token_data = {
            "sub": patient['patient_id'],
            "email": patient['email'],
            "role": patient.get('role', 'patient')
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Update last login (if function exists)
        try:
            db_helper.update_patient_last_login(patient['patient_id'])
        except:
            pass  # Ignore if function doesn't exist
        
        # Remove sensitive data
        patient_safe = {k: v for k, v in patient.items() if k != 'password_hash'}
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "patient": patient_safe
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/authenticate")
async def authenticate_patient(request: PatientAuthRequest):
    """
    Legacy authentication endpoint (for backward compatibility)
    Now requires password for email auth
    """
    try:
        patient = None
        
        if request.auth_method == "email":
            if not request.password:
                raise HTTPException(
                    status_code=400,
                    detail="Password required for email authentication"
                )
            patient = db_helper.get_patient_by_email(request.identifier)
            
            if patient and not verify_password(request.password, patient.get('password_hash', '')):
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
        elif request.auth_method == "phone":
            patient = db_helper.get_patient_by_phone(request.identifier)
        elif request.auth_method == "patient_id":
            patient = db_helper.get_patient_by_id(request.identifier)
        
        if patient:
            # Load full medical record
            full_data = {
                "patient": patient,
                "prescriptions": db_helper.get_patient_prescriptions(patient['patient_id']),
                "appointments": db_helper.get_patient_appointments(patient['patient_id']),
                "insurance": db_helper.get_patient_insurance(patient['patient_id']),
                "medical_history": db_helper.get_medical_history(patient['patient_id']),
                "lab_results": db_helper.get_lab_results(patient['patient_id'])
            }
            
            return {
                "status": "success",
                "patient": patient,
                "full_data": full_data,
                "message": f"Welcome back, {patient['first_name']}!"
            }
        else:
            return {
                "status": "new_patient",
                "message": "We don't have a record for you. Let's create one.",
                "identifier": request.identifier,
                "auth_method": request.auth_method
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register", response_model=TokenResponse)
async def register_new_patient(patient_data: NewPatientRegistration):
    """
    Register a new patient with password validation
    Returns JWT tokens
    """
    try:
        # Validate password strength
        is_valid, error_msg = validate_password_strength(patient_data.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Check if email already exists
        existing = db_helper.get_patient_by_email(patient_data.email)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists. Please sign in instead."
            )
        
        # Validate age (must be 18+)
        from datetime import datetime
        dob = datetime.strptime(patient_data.date_of_birth, '%Y-%m-%d')
        age = (datetime.now() - dob).days // 365
        if age < 18:
            raise HTTPException(
                status_code=400,
                detail="You must be at least 18 years old to create an account"
            )
        
        # Generate new patient ID
        new_patient_id = db_helper.generate_patient_id()
        
        # Hash password
        hashed_password = hash_password(patient_data.password)
        
        # Create patient record
        patient = db_helper.create_patient(
            patient_id=new_patient_id,
            first_name=patient_data.first_name,
            last_name=patient_data.last_name,
            date_of_birth=patient_data.date_of_birth,
            email=patient_data.email,
            phone=patient_data.phone,
            address=patient_data.address,
            insurance_id=patient_data.insurance_id,
            password_hash=hashed_password,
            medical_history="",
            role="patient",
            is_active=True,
            email_verified=True  # Auto-verify for now, can add email verification later
        )
        
        # Create tokens
        token_data = {
            "sub": patient['patient_id'],
            "email": patient['email'],
            "role": patient.get('role', 'patient')
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Remove sensitive data
        patient_safe = {k: v for k, v in patient.items() if k != 'password_hash'}
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "patient": patient_safe
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    from api.security import decode_token
    
    try:
        payload = decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        # Create new access token
        token_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role", "patient")
        }
        
        new_access_token = create_access_token(token_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# ============= Protected Patient Data Endpoints =============

@router.get("/me")
async def get_current_patient(current_user: dict = Depends(get_current_user)):
    """Get current authenticated patient's full data"""
    try:
        patient_id = current_user.get("patient_id")
        
        patient = db_helper.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        full_data = {
            "patient": {k: v for k, v in patient.items() if k != 'password_hash'},
            "prescriptions": db_helper.get_patient_prescriptions(patient_id),
            "appointments": db_helper.get_patient_appointments(patient_id),
            "insurance": db_helper.get_patient_insurance(patient_id),
            "medical_history": db_helper.get_medical_history(patient_id),
            "lab_results": db_helper.get_lab_results(patient_id)
        }
        
        return {
            "status": "success",
            "data": full_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/{patient_id}")
async def get_patient_full_data(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get full patient data (protected endpoint)
    Patients can only access their own data unless admin
    """
    try:
        # Check authorization
        if current_user.get("patient_id") != patient_id and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this patient's data"
            )
        
        patient = db_helper.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        full_data = {
            "patient": {k: v for k, v in patient.items() if k != 'password_hash'},
            "prescriptions": db_helper.get_patient_prescriptions(patient_id),
            "appointments": db_helper.get_patient_appointments(patient_id),
            "insurance": db_helper.get_patient_insurance(patient_id),
            "medical_history": db_helper.get_medical_history(patient_id),
            "lab_results": db_helper.get_lab_results(patient_id)
        }
        
        return {
            "status": "success",
            "data": full_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update/{patient_id}")
async def update_patient_record(
    patient_id: str,
    updates: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update patient medical record (protected)"""
    try:
        # Check authorization
        if current_user.get("patient_id") != patient_id and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Don't allow password updates through this endpoint
        if 'password_hash' in updates or 'password' in updates:
            raise HTTPException(status_code=400, detail="Use password change endpoint")
        
        updated_patient = db_helper.update_patient_record(patient_id, updates)
        
        # Remove sensitive data
        safe_patient = {k: v for k, v in updated_patient.items() if k != 'password_hash'}
        
        return {
            "status": "success",
            "patient": safe_patient,
            "message": "Medical record updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= File Upload Endpoints =============

@router.post("/upload/prescription", response_model=FileUploadResponse)
async def upload_prescription(
    file: UploadFile = File(...),
    rx_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload prescription file (image or PDF)
    Supports: JPG, PNG, PDF, HEIC
    """
    try:
        patient_id = current_user.get("patient_id")
        
        # Validate file
        validation = validate_file(file, settings.allowed_file_types, settings.max_upload_size_mb)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])
        
        # Save file
        file_info = await save_uploaded_file(
            file=file,
            patient_id=patient_id,
            category="prescriptions"
        )
        
        # Save to database
        document = db_helper.save_prescription_file(
            patient_id=patient_id,
            rx_id=rx_id,
            file_name=file_info["file_name"],
            file_path=file_info["file_path"],
            file_type=file_info["file_type"],
            file_size=file_info["file_size"],
            notes=notes
        )
        
        return FileUploadResponse(
            file_id=document["file_id"],
            file_name=document["file_name"],
            file_type=document["file_type"],
            uploaded_at=document["uploaded_at"],
            message="Prescription uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/upload/lab-result")
async def upload_lab_result(
    file: UploadFile = File(...),
    test_name: str = Form(...),
    notes: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Upload lab result document"""
    try:
        patient_id = current_user.get("patient_id")
        
        # Validate file
        validation = validate_file(file, settings.allowed_file_types, settings.max_upload_size_mb)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])
        
        # Save file
        file_info = await save_uploaded_file(
            file=file,
            patient_id=patient_id,
            category="lab_results"
        )

        ocr_text = extract_text_from_file(file_info["file_path"])
        
        # Save to database
        document = db_helper.save_lab_result_file(
            patient_id=patient_id,
            test_name=test_name,
            file_name=file_info["file_name"],
            file_path=file_info["file_path"],
            file_type=file_info["file_type"],
            file_size=file_info["file_size"],
            notes=notes
        )
        
        return {
            "status": "success",
            "file_id": document["file_id"],
            "message": "Lab result uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{patient_id}")
async def get_patient_files(
    patient_id: str,
    file_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all files for a patient (prescriptions, lab results, etc.)"""
    try:
        # Check authorization
        if current_user.get("patient_id") != patient_id and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        files = db_helper.get_patient_files(patient_id, file_type)
        
        return {
            "status": "success",
            "files": files,
            "count": len(files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/file/{file_id}")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete uploaded file"""
    try:
        # Get file info to check ownership
        file_info = db_helper.get_file_by_id(file_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check authorization
        if file_info["patient_id"] != current_user.get("patient_id") and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Delete file from filesystem
        if os.path.exists(file_info["file_path"]):
            os.remove(file_info["file_path"])
        
        # Delete from database
        db_helper.delete_file(file_id)
        
        return {
            "status": "success",
            "message": "File deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= Prescription Management (Enhanced) =============

@router.post("/prescription/update")
async def update_prescription(
    prescription_update: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update prescription status (protected)"""
    try:
        rx_id = prescription_update.get('rx_id')
        
        # Verify prescription belongs to user
        prescription = db_helper.get_prescription_by_id(rx_id)
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")
        
        if prescription["patient_id"] != current_user.get("patient_id") and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        updated_rx = db_helper.update_prescription(
            rx_id=rx_id,
            updates=prescription_update.get('updates')
        )
        
        return {
            "status": "success",
            "prescription": updated_rx,
            "message": "Prescription updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))