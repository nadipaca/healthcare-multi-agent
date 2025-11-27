"""
FINAL FIX for db_helper.py
This script will properly fix the get_or_create_session function
"""
import re

# Read the file
with open('database/db_helper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The EXACT broken code (including all whitespace)
broken_code = """        cursor.execute('''
        UPDATE chat_sessions 
        SET is_active = 0
        WHERE session_id = ? AND patient_id = ?
        ''', (session_id, patient_id))"""

# The EXACT correct code  
correct_code = """        cursor.execute('''
            SELECT session_id FROM chat_sessions 
            WHERE session_id = ? AND patient_id = ? AND is_active = 1
        ''', (session_id, patient_id))"""

# Check if broken code exists
if broken_code in content:
    # Replace it
    content = content.replace(broken_code, correct_code)
    
    # Write back
    with open('database/db_helper.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Successfully fixed db_helper.py!")
    print("   Changed UPDATE to SELECT in get_or_create_session")
else:
    print("⚠️  The exact broken code was not found.")
    print("   Checking if file is already fixed...")
    
    if correct_code in content:
        print("✅ File appears to already have the correct code!")
    else:
        print("❌ File state is unknown. Manual inspection needed.")
        # Try to find the function
        match = re.search(r'def get_or_create_session.*?return new_session\[.session_id.\]', content, re.DOTALL)
        if match:
            print("\nFound get_or_create_session function:")
            print(match.group(0)[:300] + "...")
