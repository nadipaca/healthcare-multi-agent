import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'healthcare.db')
# now points to backend/database/healthcare.db

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(prescription_files)")
    columns = [col[1] for col in cursor.fetchall()]
    if "gcs_uri" not in columns:
        cursor.execute("ALTER TABLE prescription_files ADD COLUMN gcs_uri TEXT")
        print("Added gcs_uri column to prescription_files")
    cursor.execute("DELETE FROM prescription_files")
    print("Deleted all rows from prescription_files")
    conn.commit()
    conn.close()
