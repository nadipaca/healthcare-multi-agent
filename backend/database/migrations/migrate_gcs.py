import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'healthcare.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Add gcs_uri column if missing
    cursor.execute("PRAGMA table_info(medical_documents)")
    columns = [col[1] for col in cursor.fetchall()]
    if "gcs_uri" not in columns:
        cursor.execute("ALTER TABLE medical_documents ADD COLUMN gcs_uri TEXT")
        print("✓ Added gcs_uri column to medical_documents")
    # Remove all data from medical_documents
    cursor.execute("DELETE FROM medical_documents")
    print("✓ Deleted all rows from medical_documents")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()