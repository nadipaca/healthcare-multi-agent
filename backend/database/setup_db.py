"""
Database setup script for healthcare multi-agent system
Creates tables and populates with sample patient data
"""
import sqlite3
from datetime import datetime, timedelta
import os
import sys
# Ensure backend/ is on sys.path so "api" can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Create database directory if it doesn't exist
os.makedirs(os.path.dirname(__file__), exist_ok=True)
from api.security import hash_password

DB_PATH = os.path.join(os.path.dirname(__file__), 'healthcare.db')

def setup_database():
    """Create tables and populate with sample data
       and authentication and file uploads
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Hash password for demo accounts
    demo_password = hash_password('demo2024!')  # Stronger demo password
    admin_password = hash_password('Admin@2024!')  # Strong admin password
    
    # Create Patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
             patient_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth DATE,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            address TEXT,
            insurance_id TEXT,
            medical_history TEXT,
            role TEXT DEFAULT 'patient',
            is_active BOOLEAN DEFAULT 1,
            email_verified BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Create Prescriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            file_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            rx_id TEXT,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uploaded_by TEXT,
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
            FOREIGN KEY (rx_id) REFERENCES prescriptions (rx_id)
        )
    ''')
    
    # Create Appointments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id TEXT PRIMARY KEY,
            patient_id TEXT,
            doctor_name TEXT,
            specialty TEXT,
            appointment_date DATETIME,
            reason TEXT,
            status TEXT DEFAULT 'scheduled',
            location TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    ''')
    
    # Create Insurance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS insurance (
            insurance_id TEXT PRIMARY KEY,
            patient_id TEXT,
            provider TEXT,
            policy_number TEXT,
            group_number TEXT,
            copay_primary REAL,
            copay_specialist REAL,
            deductible REAL,
            deductible_met REAL,
            coverage_status TEXT DEFAULT 'active',
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    ''')
    
    # Create Medical History table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            condition TEXT,
            diagnosed_date DATE,
            status TEXT DEFAULT 'active',
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    ''')

     # Medical Documents table
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_documents (
            document_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            document_type TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uploaded_by TEXT,
            category TEXT,
            notes TEXT,
            extracted_text TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    ''')
    
    # Create Lab Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lab_results (
            lab_id TEXT PRIMARY KEY,
            patient_id TEXT,
            test_name TEXT,
            result_value TEXT,
            unit TEXT,
            reference_range TEXT,
            test_date DATE,
            status TEXT DEFAULT 'completed',
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    ''')

    # NEW: Chat Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            title TEXT,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    ''')
    
    # NEW: Chat Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            message_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,  -- 'user' or 'assistant' or 'system'
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            agent_name TEXT,
            needs_human_review INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
        )
    ''')
    
    # Create Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            patient_id TEXT,
            rating INTEGER,
            comment TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

     # Session tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_tokens (
            token_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            refresh_token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_revoked BOOLEAN DEFAULT 0,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    ''')
    
    # Audit log for security
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            action TEXT NOT NULL,
            resource TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    ''')
    
    print("✓ Database tables created successfully")
    
    # Insert sample patients with hashed passwords
    sample_patients = [
        # Demo accounts for testing/presentation
        ('DEMO001', 'Demo', 'Patient', '1990-01-01', 'demo@healthcare.test', '555-9999',
         demo_password, 'Demo Address', 'DEMO-INS',
         'Sample medical history for demo', 'patient', 1, 1),
        
        # Admin account
        ('ADMIN001', 'System', 'Administrator', '1980-01-01', 'admin@healthcare.com', '555-0000',
         admin_password, 'Healthcare Center', None, '', 'admin', 1, 1),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO patients 
        (patient_id, first_name, last_name, date_of_birth, email, phone, 
         password_hash, address, insurance_id, medical_history, role, is_active, email_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_patients)
    
    print(f"✓ Created {len(sample_patients)} demo/admin accounts")
    print(f"\n📋 Demo Credentials (FOR TESTING ONLY):")
    print(f"   Email: demo@healthcare.test | Password: demo2024!")
    print(f"   Email: admin@healthcare.com | Password: Admin@2024!")
    print(f"\n⚠️  PRODUCTION: Users must create their own accounts via registration")
    
    
    # Insert sample prescriptions
    today = datetime.now()
    sample_prescriptions = [
        ('RX001', 'PAT001', 'Lisinopril', '10mg', 'Take 1 tablet daily', 2, 
         (today - timedelta(days=25)).strftime('%Y-%m-%d'), 'Dr. Smith', 0),
        ('RX002', 'PAT001', 'Metformin', '500mg', 'Take 1 tablet twice daily with meals', 0,
         (today - timedelta(days=85)).strftime('%Y-%m-%d'), 'Dr. Johnson', 1),
        ('RX003', 'PAT002', 'Sumatriptan', '50mg', 'Take 1 tablet at onset of migraine', 3,
         (today - timedelta(days=15)).strftime('%Y-%m-%d'), 'Dr. Lee', 0),
        ('RX004', 'PAT002', 'Albuterol Inhaler', '90mcg', 'Use as needed for breathing difficulty', 1,
         (today - timedelta(days=40)).strftime('%Y-%m-%d'), 'Dr. Lee', 0),
        ('RX005', 'PAT003', 'Ibuprofen', '600mg', 'Take 1 tablet every 8 hours as needed', 4,
         (today - timedelta(days=10)).strftime('%Y-%m-%d'), 'Dr. Brown', 0),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO prescriptions 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_prescriptions)
    
    print(f"✓ Inserted {len(sample_prescriptions)} sample prescriptions")
    
    # Insert sample appointments
    sample_appointments = [
        ('APT001', 'PAT001', 'Dr. Sarah Smith', 'Cardiology', 
         (today + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'), 
         'Follow-up for blood pressure', 'scheduled', 'Main Hospital - Cardiology Wing'),
        ('APT002', 'PAT002', 'Dr. Michael Lee', 'Neurology',
         (today + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S'),
         'Migraine management', 'scheduled', 'Neurology Center'),
        ('APT003', 'PAT003', 'Dr. Emily Brown', 'Orthopedics',
         (today + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
         'Arthritis treatment consultation', 'scheduled', 'Orthopedic Clinic'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO appointments 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_appointments)
    
    print(f"✓ Inserted {len(sample_appointments)} sample appointments")
    
    # Insert sample insurance
    sample_insurance = [
        ('INS001', 'PAT001', 'Blue Cross Blue Shield', 'BCBS123456', 'GRP001', 
         25.0, 50.0, 1500.0, 450.0, 'active'),
        ('INS002', 'PAT002', 'Aetna', 'AET987654', 'GRP002',
         30.0, 60.0, 2000.0, 800.0, 'active'),
        ('INS003', 'PAT003', 'United Healthcare', 'UHC555777', 'GRP003',
         20.0, 45.0, 1000.0, 1000.0, 'active'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO insurance 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_insurance)
    
    print(f"✓ Inserted {len(sample_insurance)} sample insurance records")
    
    # Insert sample medical history
    sample_history = [
        ('PAT001', 'Hypertension', '2018-05-10', 'active', 'Controlled with medication'),
        ('PAT001', 'Type 2 Diabetes', '2019-08-22', 'active', 'Managed with Metformin'),
        ('PAT002', 'Chronic Migraine', '2015-03-14', 'active', 'Occurs 2-3 times per month'),
        ('PAT002', 'Asthma', '2010-06-01', 'active', 'Mild, exercise-induced'),
        ('PAT003', 'Osteoarthritis', '2020-01-15', 'active', 'Primarily affects knees'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO medical_history (patient_id, condition, diagnosed_date, status, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_history)
    
    print(f"✓ Inserted {len(sample_history)} medical history records")
    
    # Insert sample lab results
    sample_labs = [
        ('LAB001', 'PAT001', 'HbA1c', '6.8', '%', '4.0-5.6', 
         (today - timedelta(days=30)).strftime('%Y-%m-%d'), 'completed'),
        ('LAB002', 'PAT001', 'Blood Pressure', '128/82', 'mmHg', '<120/80',
         (today - timedelta(days=7)).strftime('%Y-%m-%d'), 'completed'),
        ('LAB003', 'PAT002', 'Complete Blood Count', 'Normal', '', 'Normal ranges',
         (today - timedelta(days=60)).strftime('%Y-%m-%d'), 'completed'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO lab_results 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_labs)
    
    print(f"✓ Inserted {len(sample_labs)} lab results")

    # Create indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_patient ON chat_sessions(patient_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_last_message ON chat_sessions(last_message_at)')
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database setup complete! Database created at: {DB_PATH}")
    print("\nSample Patients:")
    print("  PAT001 - John Doe (Hypertension, Type 2 Diabetes)")
    print("  PAT002 - Jane Smith (Migraine, Asthma)")
    print("  PAT003 - Mike Johnson (Arthritis)")
    print("\nYou can now test all agents with this sample data!")

if __name__ == "__main__":
    setup_database()
