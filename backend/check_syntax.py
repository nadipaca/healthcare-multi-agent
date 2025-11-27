"""
Check for syntax errors in db_helper.py
"""
try:
    with open('database/db_helper.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    compile(code, 'db_helper.py', 'exec')
    print("✅ No syntax errors found!")
    
except SyntaxError as e:
    print(f"❌ Syntax Error Found:")
    print(f"   Line {e.lineno}: {e.msg}")
    print(f"   Text: {e.text}")
    print(f"   Offset: {e.offset}")
    
    # Show context
    lines = code.split('\n')
    start = max(0, e.lineno - 5)
    end = min(len(lines), e.lineno + 3)
    
    print(f"\n   Context (lines {start+1}-{end}):")
    for i in range(start, end):
        marker = " >>>" if i == e.lineno - 1 else "    "
        print(f"   {marker} {i+1:3d}: {lines[i]}")
