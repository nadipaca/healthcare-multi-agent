"""
Database helper functions for healthcare multi-agent system
"""
import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'healthcare.db')

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def dict_factory(cursor, row):
    """Convert database rows to dictionaries"""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

# Patient functions
def get_patient_by_email(email: str) -> Optional[Dict]:
    """Get patient by email"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM patients WHERE email = ?', (email,))
    patient = cursor.fetchone()
    conn.close()
    return patient

def get_patient_by_id(patient_id: str) -> Optional[Dict]:
    """Get patient by ID"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    return patient

def get_patient_by_phone(phone: str) -> Optional[Dict]:
    """Get patient by phone number"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM patients WHERE phone = ?', (phone,))
    patient = cursor.fetchone()
    conn.close()
    return patient

def generate_patient_id() -> str:
    """Generate unique patient ID"""
    import random
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    while True:
        # Generate PAT + 3 random digits
        new_id = f"PAT{random.randint(100, 999)}"
        cursor.execute('SELECT patient_id FROM patients WHERE patient_id = ?', (new_id,))
        if not cursor.fetchone():
            conn.close()
            return new_id

def create_patient(patient_id: str, first_name: str, last_name: str, 
                  date_of_birth: str, email: Optional[str], phone: Optional[str],
                  address: Optional[str], insurance_id: Optional[str], 
                  medical_history: str = "") -> Dict:
    """Create a new patient record"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO patients (patient_id, first_name, last_name, date_of_birth, 
                            email, phone, address, insurance_id, medical_history)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (patient_id, first_name, last_name, date_of_birth, email, phone, 
          address, insurance_id, medical_history))
    
    conn.commit()
    patient = get_patient_by_id(patient_id)
    conn.close()
    return patient

def update_patient_record(patient_id: str, updates: Dict) -> Dict:
    """Update patient medical record"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build dynamic UPDATE query based on provided fields
    update_fields = []
    values = []
    
    allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'address', 
                     'insurance_id', 'medical_history']
    
    for field, value in updates.items():
        if field in allowed_fields:
            update_fields.append(f"{field} = ?")
            values.append(value)
    
    if update_fields:
        values.append(patient_id)
        query = f"UPDATE patients SET {', '.join(update_fields)} WHERE patient_id = ?"
        cursor.execute(query, values)
        conn.commit()
    
    conn.close()
    patient = get_patient_by_id(patient_id)
    return patient

# Prescription functions
def get_patient_prescriptions(patient_id: str) -> List[Dict]:
    """Get all prescriptions for a patient"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM prescriptions 
        WHERE patient_id = ? 
        ORDER BY last_filled DESC
    ''', (patient_id,))
    
    prescriptions = cursor.fetchall()
    conn.close()
    return prescriptions

def request_prescription_refill(rx_id: str, patient_id: str) -> Dict:
    """Request a prescription refill"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if prescription exists and has refills
    cursor.execute('''
        SELECT medication, refills_remaining 
        FROM prescriptions 
        WHERE rx_id = ? AND patient_id = ?
    ''', (rx_id, patient_id))
    
    result = cursor.fetchone()
    if not result:
        conn.close()
        return {"status": "error", "message": "Prescription not found"}
    
    medication, refills = result
    if refills <= 0:
        conn.close()
        return {
            "status": "needs_renewal",
            "message": f"{medication} has no refills remaining. Please contact your provider."
        }
    
    # Update refill count and last filled date
    cursor.execute('''
        UPDATE prescriptions 
        SET refills_remaining = refills_remaining - 1,
            last_filled = ?
        WHERE rx_id = ?
    ''', (datetime.now().strftime('%Y-%m-%d'), rx_id))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": f"Refill request for {medication} submitted successfully!",
        "estimated_ready": "Tomorrow at 2:00 PM"
    }

# Appointment functions
def get_patient_appointments(patient_id: str) -> List[Dict]:
    """Get all appointments for a patient"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM appointments 
        WHERE patient_id = ? 
        ORDER BY appointment_date ASC
    ''', (patient_id,))
    
    appointments = cursor.fetchall()
    conn.close()
    return appointments

def create_appointment(patient_id: str, doctor: str, specialty: str, 
                      date: str, reason: str, location: str) -> Dict:
    """Create a new appointment"""
    import uuid
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    appointment_id = f"APT{str(uuid.uuid4())[:8].upper()}"
    
    cursor.execute('''
        INSERT INTO appointments 
        (appointment_id, patient_id, doctor_name, specialty, appointment_date, reason, status, location)
        VALUES (?, ?, ?, ?, ?, ?, 'scheduled', ?)
    ''', (appointment_id, patient_id, doctor, specialty, date, reason, location))
    
    conn.commit()
    conn.close()
    
    return {
        "appointment_id": appointment_id,
        "status": "BOOKED",
        "doctor": doctor,
        "specialty": specialty,
        "date": date,
        "location": location
    }

# Insurance functions
def get_patient_insurance(patient_id: str) -> Optional[Dict]:
    """Get insurance information for a patient"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM insurance 
        WHERE patient_id = ?
    ''', (patient_id,))
    
    insurance = cursor.fetchone()
    conn.close()
    return insurance

def check_insurance_eligibility(patient_id: str) -> Dict:
    """Check insurance eligibility"""
    insurance = get_patient_insurance(patient_id)
    
    if not insurance:
        return {"status": "no_insurance", "message": "No insurance on file"}
    
    if insurance['coverage_status'] != 'active':
        return {"status": "inactive", "message": "Insurance coverage is not active"}
    
    return {
        "status": "eligible",
        "provider": insurance['provider'],
        "policy_number": insurance['policy_number'],
        "copay_primary": insurance['copay_primary'],
        "copay_specialist": insurance['copay_specialist'],
        "deductible": insurance['deductible'],
        "deductible_met": insurance['deductible_met'],
        "remaining_deductible": insurance['deductible'] - insurance['deductible_met']
    }

# Medical history functions
def get_medical_history(patient_id: str) -> List[Dict]:
    """Get medical history for a patient"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM medical_history 
        WHERE patient_id = ? AND status = 'active'
        ORDER BY diagnosed_date DESC
    ''', (patient_id,))
    
    history = cursor.fetchall()
    conn.close()
    return history

# Lab results functions
def get_lab_results(patient_id: str) -> List[Dict]:
    """Get lab results for a patient"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM lab_results 
        WHERE patient_id = ? 
        ORDER BY test_date DESC
    ''', (patient_id,))
    
    results = cursor.fetchall()
    conn.close()
    return results

# Feedback functions
def save_feedback(session_id: str, patient_id: str, rating: int, 
                 comment: str, category: str) -> Dict:
    """Save patient feedback"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO feedback (session_id, patient_id, rating, comment, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, patient_id, rating, comment, category))
    
    conn.commit()
    feedback_id = cursor.lastrowid
    conn.close()
    
    return {
        "feedback_id": feedback_id,
        "status": "saved",
        "message": "Thank you for your feedback!"
    }

# Test data retrieval
def get_all_patients() -> List[Dict]:
    """Get all patients for testing"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM patients')
    patients = cursor.fetchall()
    conn.close()
    return patients
