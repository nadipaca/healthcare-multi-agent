"""
Database helper functions for healthcare multi-agent system
"""
import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime
import uuid

# ... existing imports and functions ...

# ============= Chat History Functions =============

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
                  medical_history: str = "", password_hash: Optional[str] = None,
                  role: str = "patient", is_active: bool = True, 
                  email_verified: bool = False) -> Dict:
    """Create a new patient record"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO patients (patient_id, first_name, last_name, date_of_birth, 
                            email, phone, address, insurance_id, medical_history,
                            password_hash, role, is_active, email_verified, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (patient_id, first_name, last_name, date_of_birth, email, phone, 
          address, insurance_id, medical_history, password_hash, role, 
          1 if is_active else 0, 1 if email_verified else 0))
    
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

def update_patient_last_login(patient_id: str):
    """Update patient's last login timestamp"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE patients 
        SET last_login = CURRENT_TIMESTAMP 
        WHERE patient_id = ?
    ''', (patient_id,))
    
    conn.commit()
    conn.close()

def get_prescription_files(patient_id: str) -> List[Dict]:
    """Get all prescription documents for a patient"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM prescription_files
        WHERE patient_id = ?
        ORDER BY uploaded_at DESC
        ''',
        (patient_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_prescription_file_by_id(file_id: str) -> Optional[Dict]:
    """Get a single prescription document by file_id"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM prescription_files WHERE file_id = ?',
        (file_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def save_prescription_file(
    patient_id: str,
    rx_id: Optional[str],
    file_name: str,
    file_path: str,
    file_type: str,
    file_size: int,
    notes: Optional[str] = None,
    gcs_uri: Optional[str] = None,
) -> Dict:
    """Save prescription file metadata to database"""
    import uuid

    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()

    file_id = f"FILE{str(uuid.uuid4())[:8].upper()}"

    cursor.execute('''
        INSERT INTO prescription_files
        (file_id, patient_id, rx_id, file_name, file_path, file_type, file_size, notes, gcs_uri)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (file_id, patient_id, rx_id, file_name, file_path, file_type, file_size, notes, gcs_uri))

    conn.commit()
    cursor.execute('SELECT * FROM prescription_files WHERE file_id = ?', (file_id,))
    file_record = cursor.fetchone()
    conn.close()

    return file_record

def save_lab_result_file(patient_id: str, test_name: str, file_name: str,
                         file_path: str, file_type: str, file_size: int,
                         notes: Optional[str] = None,
                         extracted_text: Optional[str] = None,
                         gcs_uri: Optional[str] = None) -> Dict:
    """Save lab result file metadata, including OCR text if provided"""
    import uuid

    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()

    file_id = f"LAB{str(uuid.uuid4())[:8].upper()}"

    cursor.execute('''
        INSERT INTO medical_documents
        (document_id, patient_id, document_type, file_name, file_path,
         file_size, category, notes, extracted_text, gcs_uri)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (file_id, patient_id, file_type, file_name, file_path, file_size, 'lab_result', notes, extracted_text, gcs_uri))

    conn.commit()

    cursor.execute('SELECT * FROM medical_documents WHERE document_id = ?', (file_id,))
    file_record = cursor.fetchone()
    conn.close()

    return file_record

def save_prescription_document_file(
    patient_id: str,
    file_name: str,
    file_path: str,
    file_type: str,
    file_size: int,
    notes: Optional[str] = None,
    extracted_text: Optional[str] = None,
    gcs_uri: Optional[str] = None,
) -> Dict:
    """Save prescription document (with optional OCR text) into medical_documents."""
    import uuid

    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()

    document_id = f"RX{str(uuid.uuid4())[:8].upper()}"

    cursor.execute(
        '''
        INSERT INTO medical_documents
        (document_id, patient_id, document_type, file_name, file_path,
         file_size, category, notes, extracted_text, gcs_uri)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            document_id,
            patient_id,
            file_type,
            file_name,
            file_path,
            file_size,
            "prescription",
            notes,
            extracted_text,
            gcs_uri,
        ),
    )

    conn.commit()
    cursor.execute('SELECT * FROM medical_documents WHERE document_id = ?', (document_id,))
    row = cursor.fetchone()
    conn.close()

    return row

def get_patient_files(patient_id: str, file_type: Optional[str] = None) -> List[Dict]:
    """Get all files for a patient"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    if file_type:
        cursor.execute('''
            SELECT * FROM medical_documents 
            WHERE patient_id = ? AND category = ?
            ORDER BY uploaded_at DESC
        ''', (patient_id, file_type))
    else:
        cursor.execute('''
            SELECT * FROM medical_documents 
            WHERE patient_id = ?
            ORDER BY uploaded_at DESC
        ''', (patient_id,))
    
    files = cursor.fetchall()
    conn.close()
    return files

def get_file_by_id(file_id: str) -> Optional[Dict]:
    """Get file metadata by ID"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM medical_documents WHERE document_id = ?', (file_id,))
    file_record = cursor.fetchone()
    conn.close()
    return file_record

def delete_file(file_id: str):
    """Delete file record from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM medical_documents WHERE document_id = ?', (file_id,))
    
    conn.commit()
    conn.close()

def get_prescription_by_id(rx_id: str) -> Optional[Dict]:
    """Get prescription by ID"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM prescriptions WHERE rx_id = ?', (rx_id,))
    prescription = cursor.fetchone()
    conn.close()
    return prescription

def get_prescription_files(patient_id: str) -> List[Dict]:
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM prescription_files
        WHERE patient_id = ?
        ORDER BY uploaded_at DESC
        ''',
        (patient_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_prescription(rx_id: str, updates: Dict) -> Dict:
    """Update prescription details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    update_fields = []
    values = []
    
    allowed_fields = ['refills_remaining', 'needs_renewal', 'last_filled', 
                     'dosage', 'instructions']
    
    for field, value in updates.items():
        if field in allowed_fields:
            update_fields.append(f"{field} = ?")
            values.append(value)
    
    if update_fields:
        values.append(rx_id)
        query = f"UPDATE prescriptions SET {', '.join(update_fields)} WHERE rx_id = ?"
        cursor.execute(query, values)
        conn.commit()
    
    conn.close()
    prescription = get_prescription_by_id(rx_id)
    return prescription

def create_chat_session(patient_id: str, initial_message: str = None) -> Dict:
    """Create a new chat session"""
    import uuid
    
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    session_id = f"session-{uuid.uuid4().hex[:16]}"
    
    # Generate a title from the first message (or use default)
    title = initial_message[:50] + "..." if initial_message and len(initial_message) > 50 else initial_message or "New Conversation"
    
    cursor.execute('''
        INSERT INTO chat_sessions (session_id, patient_id, title, created_at, last_message_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ''', (session_id, patient_id, title))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM chat_sessions WHERE session_id = ?', (session_id,))
    session = cursor.fetchone()
    conn.close()
    
    return session

def get_patient_chat_sessions(patient_id: str, limit: int = 5) -> List[Dict]:
    """Get patient's recent chat sessions"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            s.*,
            COUNT(m.message_id) as message_count,
            (SELECT content FROM chat_messages 
             WHERE session_id = s.session_id AND role = 'user' 
             ORDER BY timestamp ASC LIMIT 1) as first_message
        FROM chat_sessions s
        LEFT JOIN chat_messages m ON s.session_id = m.session_id
        WHERE s.patient_id = ? AND s.is_active = 1
        GROUP BY s.session_id
        ORDER BY s.last_message_at DESC
        LIMIT ?
    ''', (patient_id, limit))
    
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_session_messages(session_id: str) -> List[Dict]:
    """Get all messages for a session"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM chat_messages
        WHERE session_id = ?
        ORDER BY timestamp ASC
    ''', (session_id,))
    
    messages = cursor.fetchall()
    conn.close()
    return messages

def save_chat_message(
    session_id: str,
    role: str,
    content: str,
    agent_name: Optional[str] = None,
    needs_human_review: bool = False
) -> Dict:
    """Save a chat message"""
    import uuid
    
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    message_id = f"msg-{uuid.uuid4().hex[:16]}"
    
    cursor.execute('''
        INSERT INTO chat_messages 
        (message_id, session_id, role, content, agent_name, needs_human_review, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (message_id, session_id, role, content, agent_name, 1 if needs_human_review else 0))
    
    # Update session's last_message_at
    cursor.execute('''
        UPDATE chat_sessions 
        SET last_message_at = CURRENT_TIMESTAMP
        WHERE session_id = ?
    ''', (session_id,))
    
    # Update session title if it's the first user message
    if role == 'user':
        cursor.execute('''
            SELECT COUNT(*) as count FROM chat_messages 
            WHERE session_id = ? AND role = 'user'
        ''', (session_id,))
        
        count_result = cursor.fetchone()
        if count_result and count_result['count'] == 1:
            # This is the first user message - use it as title
            title = content[:50] + "..." if len(content) > 50 else content
            cursor.execute('''
                UPDATE chat_sessions 
                SET title = ?
                WHERE session_id = ?
            ''', (title, session_id))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM chat_messages WHERE message_id = ?', (message_id,))
    message = cursor.fetchone()
    conn.close()
    
    return message

def delete_chat_session(session_id: str, patient_id: str) -> bool:
    """Soft delete a chat session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify ownership
    cursor.execute('''
        SELECT patient_id FROM chat_sessions WHERE session_id = ?
    ''', (session_id,))
    
    result = cursor.fetchone()
    if not result or result[0] != patient_id:
        conn.close()
        return False
    
    # Soft delete
    cursor.execute('''
        UPDATE chat_sessions 
        SET is_active = 0
        WHERE session_id = ?
    ''', (session_id,))
    
    conn.commit()
    conn.close()
    return True

def get_or_create_session(patient_id: str, session_id: Optional[str] = None) -> str:
    """Get existing session or create new one"""
    if session_id:
        # Check if session exists and belongs to patient
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id FROM chat_sessions 
            WHERE session_id = ? AND patient_id = ? AND is_active = 1
        ''', (session_id, patient_id))
        
        existing = cursor.fetchone()
        conn.close()
        
        if existing:
            return session_id
    
    # Create new session
    new_session = create_chat_session(patient_id)
    return new_session['session_id']
