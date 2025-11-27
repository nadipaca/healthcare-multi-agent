"""
Ultimate fix - using sed-style replacement with line numbers
"""

# Read all lines
with open('database/db_helper.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines 604-606 (0-indexed: 603-605) need to be replaced
# Current (broken):
# Line 604:         UPDATE chat_sessions 
# Line 605:         SET is_active = 0
# Line 606:         WHERE session_id = ? AND patient_id = ?

# New (correct):
# Line 604:             SELECT session_id FROM chat_sessions 
# Line 605:             WHERE session_id = ? AND patient_id = ? AND is_active = 1

# Replace lines 604-606 with the corrected version
lines[603] = "        cursor.execute('''\n"
lines[604] = "            SELECT session_id FROM chat_sessions \n"
lines[605] = "            WHERE session_id = ? AND patient_id = ? AND is_active = 1\n"
lines[606] = "        ''', (session_id, patient_id))\n"

# Write back
with open('database/db_helper.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fixed db_helper.py using line replacement!")
print("   Lines 604-606 corrected")

# Verify
try:
    with open('database/db_helper.py', 'r') as f:
        code = f.read()
    compile(code, 'db_helper.py', 'exec')
    print("✅ Syntax check PASSED!")
except SyntaxError as e:
    print(f"❌ Still has syntax error on line {e.lineno}: {e.msg}")
