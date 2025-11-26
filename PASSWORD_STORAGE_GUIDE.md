# Authentication Password Storage Flow

## Overview
Passwords in your healthcare multi-agent system are **NEVER stored in plain text**. They are always hashed using bcrypt before storage.

---

## 📍 Password Storage Locations

### 1. **Database Storage** (SQLite)
**File:** `backend/database/healthcare.db`
**Table:** `patients`
**Column:** `password_hash` (TEXT NOT NULL)

```sql
CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth DATE,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    password_hash TEXT NOT NULL,  ← HASHED PASSWORD STORED HERE
    address TEXT,
    insurance_id TEXT,
    medical_history TEXT,
    role TEXT DEFAULT 'patient',
    is_active BOOLEAN DEFAULT 1,
    email_verified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
```

**Example of stored hash:**
```
$2b$12$KIXxT4c3NqR7lLPY5dH7aeVZN8xF5FvGLq5RjPq7VwN9kL3xD7CyG
```
This is a bcrypt hash - **it cannot be reversed to get the original password**.

---

## 🔐 Password Hashing Functions

### **File:** `backend/api/security.py`

#### Hash Password Function (Lines 12-15)
```python
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)  # Default: 12 rounds
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
```

**What happens:**
1. Takes plain text password
2. Generates a random salt with 12 rounds (configurable in `config.py`)
3. Uses bcrypt to hash password + salt
4. Returns the hash as a string

#### Verify Password Function (Lines 17-22)
```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
```

**What happens:**
1. Takes user's plain text password input
2. Takes stored hash from database
3. Uses bcrypt to check if they match
4. Returns True/False

---

## 🔄 Complete Authentication Flow

### **Registration Flow** (New User)

**File:** `backend/api/patient_routes.py`
**Function:** `register_new_patient()` (Lines 215-291)

```
User enters password
        ↓
Frontend sends to backend (HTTPS encrypted)
        ↓
Backend validates password strength
        ↓
hash_password() called (security.py)
        ↓
Bcrypt creates hash with salt
        ↓
Hashed password stored in database
        ↓
Original password is DISCARDED
```

**Code snippet:**
```python
@router.post("/register", response_model=TokenResponse)
async def register_new_patient(patient_data: NewPatientRegistration):
    # Step 1: Validate password strength
    is_valid, error_msg = validate_password_strength(patient_data.password)
    
    # Step 2: Hash the password
    hashed_password = hash_password(patient_data.password)  ← HASHING HAPPENS HERE
    
    # Step 3: Store in database
    patient = db_helper.create_patient(
        patient_id=new_patient_id,
        # ... other fields ...
        password_hash=hashed_password,  ← ONLY HASH IS STORED
    )
    
    # Step 4: Original password is gone from memory
    # Step 5: Return JWT tokens (no password)
```

---

### **Login Flow** (Existing User)

**File:** `backend/api/patient_routes.py`
**Function:** `login()` (Lines 86-158)

```
User enters email + password
        ↓
Frontend sends to backend (HTTPS encrypted)
        ↓
Backend retrieves patient record by email
        ↓
Gets password_hash from database
        ↓
verify_password() called (security.py)
        ↓
Bcrypt compares plain password with hash
        ↓
If match: Create JWT tokens
        ↓
If no match: Return error
```

**Code snippet:**
```python
@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    # Step 1: Get patient from database
    patient = db_helper.get_patient_by_email(credentials.email)
    
    # Step 2: Get stored hash
    password_hash = patient.get('password_hash')
    
    # Step 3: Verify password
    if not verify_password(credentials.password, password_hash):  ← VERIFICATION HERE
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Step 4: Create JWT tokens (no password in tokens)
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Step 5: Return tokens (hashed password removed)
    patient_safe = {k: v for k, v in patient.items() if k != 'password_hash'}
```

---

## 📂 File Locations Summary

| What | File Path | Lines |
|------|-----------|-------|
| **Password Hashing** | `backend/api/security.py` | 12-22 |
| **Password Verification** | `backend/api/security.py` | 17-22 |
| **Registration Endpoint** | `backend/api/patient_routes.py` | 215-291 |
| **Login Endpoint** | `backend/api/patient_routes.py` | 86-158 |
| **Database Storage** | `backend/database/healthcare.db` | Table: `patients`, Column: `password_hash` |
| **Database Schema** | `backend/database/setup_db.py` | 27-45 |
| **Database Helper** | `backend/database/db_helper.py` | Function: `create_patient()` |
| **Bcrypt Config** | `backend/api/config.py` | `bcrypt_rounds: int = 12` |

---

## 🔒 Security Features

### 1. **Bcrypt Hashing**
- **Algorithm:** bcrypt (industry standard)
- **Rounds:** 12 (configurable in `config.py`)
- **Salt:** Automatically generated per password
- **One-way:** Cannot reverse the hash to get original password

### 2. **Password Validation** (Lines 61-82 in `patient_routes.py`)
```python
def validate_password_strength(password: str):
    """
    Validate password strength
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return (False, "Password must be at least 8 characters long")
    
    if not any(char.isupper() for char in password):
        return (False, "Password must contain at least one uppercase letter")
    
    if not any(char.islower() for char in password):
        return (False, "Password must contain at least one lowercase letter")
    
    if not any(char.isdigit() for char in password):
        return (False, "Password must contain at least one number")
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(char in special_chars for char in password):
        return (False, "Password must contain at least one special character")
    
    return (True, None)
```

### 3. **Never Returned to Client**
```python
# Password hash is always removed before sending to frontend
patient_safe = {k: v for k, v in patient.items() if k != 'password_hash'}
```

### 4. **JWT Tokens** (Not Passwords)
After login, the system uses JWT tokens for authentication:
- **Access Token:** Short-lived (1 hour)
- **Refresh Token:** Longer-lived (7 days)
- **No passwords in tokens**

---

## ⚠️ Important Notes

1. **Plain text passwords are NEVER stored anywhere**
2. **Passwords are only in memory briefly during registration/login**
3. **Hashed passwords cannot be reversed**
4. **If a user forgets their password, you must reset it (create new hash)**
5. **The database only contains bcrypt hashes**

---

## 🧪 Example Data

**Demo Account:**
- Email: `demo@healthcare.test`
- Password: `demo2024!`
- Stored in DB: `$2b$12$...` (bcrypt hash)

**Location in code:**
- File: `backend/database/setup_db.py`
- Lines: 23, 214-216

```python
demo_password = hash_password('demo2024!')  # Creates bcrypt hash

sample_patients = [
    ('DEMO001', 'Demo', 'Patient', '1990-01-01', 'demo@healthcare.test', '555-9999',
     demo_password,  # ← This is already hashed!
     'Demo Address', 'DEMO-INS', 'Sample medical history for demo', 'patient', 1, 1),
]
```

---

## 🔍 How to View/Debug (For Development Only)

**To see what's in the database:**
```python
import sqlite3
conn = sqlite3.connect('backend/database/healthcare.db')
cursor = conn.cursor()
cursor.execute("SELECT patient_id, email, password_hash FROM patients")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()
```

**Output will look like:**
```
('DEMO001', 'demo@healthcare.test', '$2b$12$KIXxT4c3NqR7lLPY5dH7aeVZN8xF5FvGLq5RjPq7VwN9kL3xD7CyG')
```

You'll see the hash but **never the original password**.

---

## Summary

✅ Passwords are **hashed with bcrypt** before storage
✅ Stored in **SQLite database** in `password_hash` column
✅ **Never** stored in plain text
✅ **Never** sent to frontend
✅ Hashing happens in `backend/api/security.py`
✅ Storage happens via `backend/database/db_helper.py`
✅ Database table: `patients` (column: `password_hash`)
