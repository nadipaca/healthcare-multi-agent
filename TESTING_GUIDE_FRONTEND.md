# 🧪 Frontend Testing Guide - Healthcare Multi-Agent System

## Quick Start Testing from localhost:5173

### Prerequisites ✅
- ✅ Database created with sample data (healthcare.db)
- ✅ Backend running on localhost:8000
- ✅ Frontend running on localhost:5173

---

## Step-by-Step Testing Instructions

### 1️⃣ Start the Backend Server
```powershell
cd backend
.venv\Scripts\activate
python run.py
```
**Expected:** Server running at `http://localhost:8000`

### 2️⃣ Start the Frontend Server
```powershell
cd frontend
npm run dev
```
**Expected:** Frontend running at `http://localhost:5173`

### 3️⃣ Open Browser and Navigate
Go to: **http://localhost:5173**

---

## 🎯 Testing Scenarios

### Test Patient Profiles

#### **PAT001 - John Doe** (Chronic Conditions)
- **Conditions:** Hypertension, Type 2 Diabetes
- **Prescriptions:** 
  - Metformin 500mg (60 refills left)
  - Lisinopril 10mg (0 refills - needs renewal!)
- **Insurance:** Blue Cross Blue Shield ($3000 deductible met)
- **Use for:** Prescription refill testing

#### **PAT002 - Jane Smith** (Acute/Recurring)
- **Conditions:** Migraine, Asthma
- **Prescriptions:** 
  - Sumatriptan 50mg (15 refills)
  - Albuterol inhaler (30 refills)
- **Insurance:** Aetna ($1500 deductible partially met)
- **Use for:** Symptom checking, specialty routing

#### **PAT003 - Mike Johnson** (Orthopedic)
- **Conditions:** Arthritis
- **Prescriptions:** 
  - Ibuprofen 800mg (45 refills)
- **Insurance:** UnitedHealthcare ($5000 deductible fully met)
- **Use for:** Appointment scheduling, insurance verification

---

## 🧪 Recommended Test Scenarios

### Scenario 1: Prescription Refill (PAT001)
1. **Select Patient:** John Doe (PAT001)
2. **Chat Message:** "I need to refill my blood pressure medication"
3. **Expected Flow:**
   - Agent identifies Lisinopril (0 refills remaining)
   - Suggests contacting provider for new prescription
   - Offers appointment scheduling

### Scenario 2: Symptom Check with History (PAT002)
1. **Select Patient:** Jane Smith (PAT002)
2. **Chat Message:** "I'm having a severe headache with light sensitivity"
3. **Expected Flow:**
   - Agent recognizes migraine history
   - Routes to neurology specialty
   - Suggests immediate relief options
   - Offers appointment with neurologist

### Scenario 3: New Symptom (PAT003)
1. **Select Patient:** Mike Johnson (PAT003)
2. **Chat Message:** "My knee has been hurting when I walk"
3. **Expected Flow:**
   - Agent assesses urgency
   - Recognizes arthritis history
   - Routes to orthopedics
   - Checks insurance coverage for orthopedic visits

### Scenario 4: Appointment Scheduling (Any Patient)
1. **Select any patient**
2. **Chat Message:** "I need to schedule an appointment with a cardiologist"
3. **Expected Flow:**
   - Shows available time slots
   - Confirms patient insurance coverage
   - Books appointment
   - Provides preparation instructions

### Scenario 5: Insurance Check (PAT003)
1. **Select Patient:** Mike Johnson (PAT003)
2. **Chat Message:** "Will my insurance cover a specialist visit?"
3. **Expected Flow:**
   - Retrieves insurance details (UnitedHealthcare)
   - Shows deductible status ($5000 met - fully covered!)
   - Displays copay amount ($50)
   - Explains coverage benefits

### Scenario 6: Feedback Collection (Any Patient)
1. **Select any patient**
2. **Chat Message:** "I want to give feedback about my recent visit"
3. **Expected Flow:**
   - Asks about experience rating
   - Collects specific feedback
   - Records in database
   - Thanks patient

---

## 🔍 What to Look For

### ✅ Success Indicators
- [ ] Patient selector displays 3 test patients with medical history
- [ ] Selected patient banner shows at top of chat
- [ ] Patient data cards show correct counts (prescriptions, appointments, etc.)
- [ ] Agent responses include patient-specific information
- [ ] Proactive action suggestions appear after agent responses
- [ ] Agent trace shows which agent is handling the request
- [ ] Prescriptions mention actual medication names from database
- [ ] Insurance details match patient's actual coverage

### 🔴 Things to Debug
- CORS errors in browser console
- "No response" or empty messages
- Wrong patient data appearing
- Missing prescription/insurance details
- Agent not routing to correct specialty

---

## 🎨 UI Features to Test

### Patient Selector Component
- **Location:** Top of chat page
- **Features:**
  - Click any patient card to select
  - Selected patient highlighted in blue
  - Patient data overview cards appear below
  - Shows counts for prescriptions, appointments, lab results

### Patient Data Cards
- **Prescriptions Card:** Shows total count + how many need renewal
- **Appointments Card:** Shows upcoming visit count
- **Insurance Card:** Provider name + copay amount
- **Conditions Card:** Number of active conditions
- **Lab Results Card:** Recent test count

### Proactive Actions
- **Trigger:** After agent completes a response
- **Appears:** Green banner above chat with suggested next steps
- **Click:** Automatically fills input with the suggested action

### Test Scenarios Panel
- **Location:** Bottom of patient selector
- **Shows:** Suggested test messages for each agent type
- **Format:** Scenario description + example message + expected flow

---

## 🐛 Common Issues & Solutions

### Issue: "Failed to fetch patients"
**Solution:** Backend not running. Start with `python run.py`

### Issue: CORS error in console
**Solution:** Check that frontend is on port 5173 or 5174 (configured in backend)

### Issue: Patient data not loading
**Solution:** Run `python backend/database/setup_db.py` to create database

### Issue: Agents returning generic responses
**Solution:** Tools might not be using database yet - check tool implementations

### Issue: Selected patient not affecting responses
**Solution:** Check that patient_id is being sent in API request payload

---

## 📊 API Endpoints to Verify

### Test Patient Selection
```bash
# List all patients
curl http://localhost:8000/api/testing/patients

# Get specific patient data
curl http://localhost:8000/api/testing/patient/PAT001

# Select patient for session
curl -X POST http://localhost:8000/api/testing/select-patient \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "PAT001"}'
```

### Test Chat with Patient Context
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "I need to refill my medication",
    "patient_id": "PAT001"
  }'
```

---

## 🎯 Next Steps After Testing

1. **Update Agent Tools** - Integrate database helpers into tool implementations
2. **Add More Test Data** - Create additional patients with different scenarios
3. **Implement Context Persistence** - Store selected patient in session
4. **Add Visual Indicators** - Show when agent is accessing database
5. **Error Handling** - Add better error messages for missing data

---

## 📝 Testing Checklist

- [ ] Backend server running without errors
- [ ] Frontend loads at localhost:5173
- [ ] 3 test patients display in selector
- [ ] Can select each patient successfully
- [ ] Patient data cards populate correctly
- [ ] Test scenarios section shows suggested messages
- [ ] Can send chat messages
- [ ] Agent responses appear
- [ ] Try prescription refill scenario (PAT001)
- [ ] Try symptom check scenario (PAT002)
- [ ] Try insurance verification (PAT003)
- [ ] Try appointment scheduling (any patient)
- [ ] Try feedback collection (any patient)
- [ ] Proactive actions appear and work
- [ ] Agent trace shows active agent
- [ ] New chat button resets conversation

---

## 🚀 Power User Tips

1. **Quick Patient Switch:** Select different patients mid-conversation to test context switching
2. **Complex Scenarios:** Combine multiple requests: "I have a headache, check my insurance, and schedule an appointment"
3. **Edge Cases:** Test with expired prescriptions, met deductibles, multiple conditions
4. **Flow Continuity:** Follow suggested actions to test multi-step workflows
5. **Database Inspection:** Use DB Browser for SQLite to verify data changes

---

Happy Testing! 🎉

For issues, check:
- Browser console (F12) for errors
- Backend terminal for Python errors
- Network tab for failed API requests
