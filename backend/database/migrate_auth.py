"""
Migration script to add authentication fields to existing database
"""
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api.security import hash_password

DB_PATH = os.path.join(os.path.dirname(__file__), 'healthcare.db')

def migrate_database():
    """Add password_hash and authentication fields to existing patients table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(patients)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    print(f"Existing columns: {existing_columns}")
    
    # Add missing columns if they don't exist
    if 'password_hash' not in existing_columns:
        print("Adding password_hash column...")
        cursor.execute("ALTER TABLE patients ADD COLUMN password_hash TEXT")
        
        # Set default password for existing patients
        default_password = hash_password("password123")
        cursor.execute("UPDATE patients SET password_hash = ? WHERE password_hash IS NULL", (default_password,))
        print("✓ Added password_hash column (default password: password123)")
    
    if 'role' not in existing_columns:
        print("Adding role column...")
        cursor.execute("ALTER TABLE patients ADD COLUMN role TEXT DEFAULT 'patient'")
        cursor.execute("UPDATE patients SET role = 'patient' WHERE role IS NULL")
        print("✓ Added role column")
    
    if 'is_active' not in existing_columns:
        print("Adding is_active column...")
        cursor.execute("ALTER TABLE patients ADD COLUMN is_active BOOLEAN DEFAULT 1")
        cursor.execute("UPDATE patients SET is_active = 1 WHERE is_active IS NULL")
        print("✓ Added is_active column")
    
    if 'email_verified' not in existing_columns:
        print("Adding email_verified column...")
        cursor.execute("ALTER TABLE patients ADD COLUMN email_verified BOOLEAN DEFAULT 0")
        cursor.execute("UPDATE patients SET email_verified = 1 WHERE email_verified IS NULL")
        print("✓ Added email_verified column")
    
    if 'created_at' not in existing_columns:
        print("Adding created_at column...")
        cursor.execute("ALTER TABLE patients ADD COLUMN created_at TIMESTAMP")
        # Set current timestamp for existing patients
        cursor.execute("UPDATE patients SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        print("✓ Added created_at column")
    
    if 'last_login' not in existing_columns:
        print("Adding last_login column...")
        cursor.execute("ALTER TABLE patients ADD COLUMN last_login TIMESTAMP")
        print("✓ Added last_login column")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database migration complete!")
    print("\n📋 Default credentials for existing patients:")
    print("   Password: password123")

if __name__ == "__main__":
    migrate_database()
