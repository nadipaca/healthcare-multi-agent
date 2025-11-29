# Testing Rate Limiter & Analytics Dashboard

## 🎯 Quick Start

### 1. Start the Server
```powershell
cd d:\workspace\healthcare-multi-agent\backend
python run.py
```

### 2. Test Rate Limiter
```powershell
.\tests\test_rate_limiter.ps1
```

**Expected Results:**
- First 20 requests: ✓ Success (Green)
- Requests 21-25: ✗ Rate Limited (429 Too Many Requests)
- Shows remaining requests per minute/hour

### 3. Test Analytics System
```powershell
.\tests\test_analytics.ps1
```

**Expected Results:**
- Creates 3 test sessions with multiple interactions
- Shows dashboard metrics (total interactions, active sessions, HITL flags)
- Displays agent usage breakdown
- Shows agent performance (avg duration, ratings, HITL rate)
- Lists top active sessions

### 4. View Dashboard in Browser

**Option A: Simple Browser Preview**
1. Open `backend/dashboard.html` in VS Code
2. Right-click → "Open with Live Server" (if installed)
   OR double-click to open in your browser

**Option B: File Path**
```
file:///d:/workspace/healthcare-multi-agent/backend/dashboard.html
```

**Dashboard Features:**
- 📊 Real-time metrics (auto-refreshes every 30 seconds)
- 🎨 Beautiful gradient design
- 📈 Visual bar charts for agent usage
- 🚩 HITL flag monitoring
- ⏱️ Time range selector (1h, 6h, 24h, 7d)

---

## 📡 API Endpoints Reference

### Chat Endpoint (with Rate Limiting & Analytics)
```powershell
$body = @{
    session_id = "your-session-id"
    message = "I have a headache"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"
```

### Analytics Dashboard (GET)
```powershell
# Last 24 hours (default)
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/dashboard?hours=24" -Method Get

# Last hour
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/dashboard?hours=1" -Method Get
```

**Response Structure:**
```json
{
  "overview": {
    "total_interactions": 42,
    "active_sessions": 8,
    "hitl_flags": 3,
    "avg_session_duration_seconds": 156.5,
    "time_period_hours": 24
  },
  "agent_usage": {
    "symptom_agent": 20,
    "appointment_agent": 15,
    "insurance_agent": 7
  },
  "agent_performance": {
    "symptom_agent": {
      "avg_duration_ms": 1234.5,
      "avg_rating": 4.5,
      "hitl_rate": 15.0
    }
  },
  "top_sessions": [...],
  "recent_hitl_flags": [...]
}
```

### Session Details (GET)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/session/your-session-id" -Method Get
```

**Response:**
```json
{
  "session_id": "your-session-id",
  "total_interactions": 5,
  "unique_agents": 2,
  "hitl_flags": 1,
  "average_rating": 4.5,
  "duration_minutes": 3.2,
  "interactions": [...]
}
```

### Rate Limit Check (GET)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/rate-limits/your-session-id" -Method Get
```

**Response:**
```json
{
  "session_id": "your-session-id",
  "remaining_per_minute": 15,
  "remaining_per_hour": 95
}
```

### Submit Rating (POST)
```powershell
$body = @{
    session_id = "your-session-id"
    rating = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/feedback/rating" -Method Post -Body $body -ContentType "application/json"
```

---

## 🔧 Rate Limiter Configuration

Located in: `backend/api/rate_limiter.py`

**Current Limits:**
- **Per Minute:** 20 requests
- **Per Hour:** 100 requests

**To Adjust:**
```python
rate_limiter = RateLimiter(
    requests_per_minute=20,  # Change this
    requests_per_hour=100     # Change this
)
```

**Error Response (429):**
```json
{
  "detail": "Rate limit exceeded. Try again in X seconds.",
  "retry_after": 45
}
```

---

## 📊 Analytics Configuration

Located in: `backend/api/analytics.py`

**Tracked Metrics:**
- Total interactions per agent
- Average response time (ms)
- User ratings (1-5 stars)
- HITL flag rate
- Session duration
- Active sessions
- Agent usage patterns

**Storage:** In-memory (for demo purposes)

**To Add Persistence:**
```python
# Replace in-memory lists with database
# Example: SQLite, PostgreSQL, MongoDB
```

---

## 🧪 Test Scenarios

### Scenario 1: Normal Usage
```powershell
# Single request - should succeed
$body = @{ session_id = "test-1"; message = "I have a fever" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"
```

### Scenario 2: Rate Limit Testing
```powershell
# Run the automated test
.\tests\test_rate_limiter.ps1
```

### Scenario 3: Multi-Agent Workflow
```powershell
$sessionId = "workflow-test"

# Step 1: Symptom check
$body = @{ session_id = $sessionId; message = "I have chest pain" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"

# Step 2: Schedule appointment
$body = @{ session_id = $sessionId; message = "Schedule appointment with cardiologist" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"

# Step 3: Check insurance
$body = @{ session_id = $sessionId; message = "Is this covered by my insurance?" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"

# View session analytics
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/session/$sessionId" -Method Get
```

### Scenario 4: Load Testing
```powershell
# Create multiple concurrent sessions
1..10 | ForEach-Object -Parallel {
    $body = @{ 
        session_id = "load-test-$_"
        message = "Test message $_"
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"
}

# Check dashboard
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/dashboard" -Method Get
```

---

## 🎥 Demo Script for Hackathon

### 1. **Show Dashboard** (1 min)
- Open `dashboard.html` in browser
- Point out real-time metrics
- Explain auto-refresh feature

### 2. **Demonstrate Multi-Agent Flow** (2 min)
```powershell
$demo = "hackathon-demo"

# Symptom check
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body (@{session_id=$demo; message="I have severe headache and nausea"} | ConvertTo-Json) -ContentType "application/json"

# Schedule appointment
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body (@{session_id=$demo; message="Schedule urgent appointment"} | ConvertTo-Json) -ContentType "application/json"

# Check insurance
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body (@{session_id=$demo; message="Will insurance cover this?"} | ConvertTo-Json) -ContentType "application/json"
```

### 3. **Show Rate Limiting** (1 min)
```powershell
.\tests\test_rate_limiter.ps1
```
- Explain production-ready feature
- Prevents API abuse
- Shows graceful degradation

### 4. **Analytics Deep Dive** (1 min)
- Refresh dashboard
- Show session details
- Explain HITL flags
- Demonstrate agent performance metrics

### 5. **Architecture Highlight** (1 min)
**Key Points:**
- ✅ Multi-agent orchestration (Google ADK)
- ✅ Rate limiting (production-ready)
- ✅ Analytics & monitoring
- ✅ HITL flagging for safety
- ✅ Session management
- ✅ Comprehensive testing (21 unit tests)

---

## 🚨 Troubleshooting

### Dashboard Not Loading?
**Check:**
1. Server is running: `http://localhost:8000`
2. CORS is enabled in `main.py`
3. Browser console for errors (F12)

**Fix:**
```python
# In api/main.py - should already be there
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting Not Working?
**Verify:**
```powershell
# Check rate limit status
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/rate-limits/test-session" -Method Get
```

### No Analytics Data?
**Generate Test Data:**
```powershell
.\tests\test_analytics.ps1
```

---

## 📝 Next Steps

### For Hackathon Enhancement:
1. ✅ **Rate Limiter** - DONE
2. ✅ **Analytics Dashboard** - DONE
3. 🔄 **Emergency Triage Agent** - HIGH PRIORITY
4. 🔄 **Prescription Refill Agent** - PRACTICAL
5. 🔄 **Database Persistence** - SCALABILITY

### To Implement Emergency Agent:
```powershell
# Create the agent file
New-Item -Path "backend\adk_app\emergency_agent.py" -ItemType File

# Add to orchestrator routing
# Edit: backend/adk_app/orchestrator_agent.py
```

---

## 🎯 Success Metrics

**Your System Now Has:**
- ✅ 21 passing unit tests
- ✅ Rate limiting (20/min, 100/hour)
- ✅ Real-time analytics dashboard
- ✅ 4 working agents (symptom, appointment, insurance, feedback)
- ✅ Session management
- ✅ HITL flagging
- ✅ Performance monitoring
- ✅ User rating system

**Impressive Stats for Portfolio:**
- Multi-agent orchestration
- Production-ready features
- Comprehensive testing
- Real-time monitoring
- Scalable architecture

---

## 📖 Documentation for Judges

**Highlight These Points:**
1. **Safety First:** HITL flagging for critical symptoms
2. **Production Ready:** Rate limiting & monitoring
3. **User Experience:** Seamless multi-agent routing
4. **Data-Driven:** Analytics for continuous improvement
5. **Tested:** 21 unit tests with 100% pass rate

**Live Demo Flow:**
1. Show dashboard → Visual appeal
2. Run multi-agent test → Technical depth
3. Trigger rate limit → Production thinking
4. Show HITL flag → Safety consideration
5. Display metrics → Data-driven approach

---

Good luck with your hackathon! 🚀
