"""
Quick fix script for db_helper.py get_or_create_session function
"""

# Read the file
with open('database/db_helper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the broken function
broken_function = """def get_or_create_session(patient_id: str, session_id: Optional[str] = None) -> str:
    \"\"\"Get existing session or create new one\"\"\"
    if session_id:
        # Check if session exists and belongs to patient
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE chat_sessions 
        SET is_active = 0
        WHERE session_id = ? AND patient_id = ?
        ''', (session_id, patient_id))
        
        existing = cursor.fetchone()
        conn.close()
        
        if existing:
            return session_id
    
    # Create new session
    new_session = create_chat_session(patient_id)
    return new_session['session_id']"""

correct_function = """def get_or_create_session(patient_id: str, session_id: Optional[str] = None) -> str:
    \"\"\"Get existing session or create new one\"\"\"
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
    return new_session['session_id']"""

# Replace
content = content.replace(broken_function, correct_function)

# Write back
with open('database/db_helper.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed get_or_create_session function!")
print("  - Changed UPDATE to SELECT")
print("  - Function now correctly checks if session exists")
