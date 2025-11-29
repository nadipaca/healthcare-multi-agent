"""
Proper fix for db_helper.py - line by line replacement
"""

# Read all lines
with open('database/db_helper.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with UPDATE and replace it with SELECT
modified = False
for i, line in enumerate(lines):
    if i >= 603 and i <= 606:  # Lines 604-607 (0-indexed: 603-606)
        if 'UPDATE chat_sessions' in line:
            lines[i] = '            SELECT session_id FROM chat_sessions \n'
            modified = True
        elif 'SET is_active = 0' in line:
            lines[i] = '            WHERE session_id = ? AND patient_id = ? AND is_active = 1\n'
            modified = True
        elif 'WHERE session_id = ? AND patient_id = ?' in line and 'UPDATE' in lines[i-1]:
            lines[i] = ''  # Remove this line as it's now part of the SELECT
            modified = True

# Write back
with open('database/db_helper.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

if modified:
    print("✅ Successfully fixed db_helper.py!")
    print("  - Replaced UPDATE with SELECT in get_or_create_session")
else:
    print("⚠️  Could not find the problematic lines. File may already be fixed.")
