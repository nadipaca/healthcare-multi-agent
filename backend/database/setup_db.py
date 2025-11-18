"""
Database setup script for healthcare multi-agent system
Creates tables and populates with sample patient data
"""
import sqlite3
from datetime import datetime, timedelta
import os

# Create database directory if it doesn't exist
os.makedirs(os.path.dirname(__file__), exist_ok=True)

DB_PATH = os.path.join(os.path.dirname(__file__), 'healthcare.db')

def setup_database():
    """Create tables and populate with sample data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth DATE,
            email TEXT,
            phone TEXT,
            address TEXT,
            insurance_id TEXT,
            medical_history TEXT
        )
    ''')
    
    # Create Prescriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            rx_id TEXT PRIMARY KEY,
            patient_id TEXT,
            medication TEXT NOT NULL,
            dosage TEXT,
            instructions TEXT,
            refills_remaining INTEGER,
            last_filled DATE,
            prescriber TEXT,
            needs_renewal BOOLEAN DEFAULT 0,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
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
    
    print("✓ Database tables created successfully")
    
    # Insert sample patients
    sample_patients = [
        ('PAT001', 'John', 'Doe', '1985-03-15', 'john.doe@email.com', '555-0101', 
         '123 Main St, City, State 12345', 'INS001', 'Hypertension, Type 2 Diabetes'),
        ('PAT002', 'Jane', 'Smith', '1990-07-22', 'jane.smith@email.com', '555-0102',
         '456 Oak Ave, City, State 12345', 'INS002', 'Migraine, Asthma'),
        ('PAT003', 'Mike', 'Johnson', '1978-11-08', 'mike.j@email.com', '555-0103',
         '789 Pine Rd, City, State 12345', 'INS003', 'Arthritis'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO patients 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_patients)
    
    print(f"✓ Inserted {len(sample_patients)} sample patients")
    
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
