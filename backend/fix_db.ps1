# Read file
$content = Get-Content 'database\db_helper.py'

# Find and replace the specific lines
$newContent = @()
$inBadSection = $false

for ($i = 0; $i -lt $content.Length; $i++) {
    $lineNum = $i + 1
    $line = $content[$i]
    
    # Lines 604-607 need fixing
    if ($lineNum -eq 604 -and $line -match 'UPDATE chat_sessions') {
        # Replace lines 604-607
        $newContent += "            SELECT session_id FROM chat_sessions "
        $newContent += "            WHERE session_id = ? AND patient_id = ? AND is_active = 1"
        $newContent += "        ''', (session_id, patient_id))"
        # Skip the next 3 lines (605, 606, 607)
        $i += 3
    } else {
        $newContent += $line
    }
}

# Write back
$newContent | Set-Content 'database\db_helper.py'

Write-Host "✅ Fixed db_helper.py!"
