# Appointment Agent API Testing - PowerShell Commands

## ✅ WORKING COMMANDS

The appointment agent is now fully functional through the API endpoint!

### 1. Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

### 2. Appointment Agent Tests

#### Basic Appointment Request:
```powershell
$body = '{"message":"I need to schedule an appointment","session_id":"test-1"}'
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"
```

#### Book Appointment with Specialty:
```powershell
$body = '{"message":"Book an appointment for orthopedics","session_id":"test-2"}'
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"
```

#### Schedule a Visit:
```powershell
$body = '{"message":"Schedule a visit for tomorrow","session_id":"test-3"}'
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"
```

#### Book an Appointment (alternative keyword):
```powershell
$body = '{"message":"book a visit","session_id":"test-4"}'
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"
```

### 3. Symptom Checker Tests (for comparison)

#### Test Symptom Agent:
```powershell
$body = '{"message":"I have knee pain when walking","session_id":"symptom-1"}'
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"
```

## Keywords that Trigger Appointment Agent

The orchestrator routes to the appointment agent when it detects these keywords:
- "appointment"
- "schedule"
- "book a visit"
- "book an appointment"

Any other message goes to the symptom checker.

## How It Works

1. **User sends message** → FastAPI endpoint `/api/chat`
2. **Orchestrator Agent** analyzes the message
3. **Routes to appropriate agent:**
   - Contains appointment keywords → **Appointment Agent**
   - Otherwise → **Symptom Agent**
4. **Agent processes** and returns response
5. **Response sent back** to user

## Full Conversation Example

```powershell
# Request 1: Initial appointment request
$body1 = '{"message":"I want to schedule an appointment","session_id":"conversation-1"}'
$response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body1 -ContentType "application/json"
Write-Host "Agent:" $response1.messages

# Request 2: Provide details
$body2 = '{"message":"I need orthopedics for knee pain","session_id":"conversation-1"}'
$response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body2 -ContentType "application/json"
Write-Host "Agent:" $response2.messages

# Request 3: Select slot
$body3 = '{"message":"Book the first available slot","session_id":"conversation-1"}'
$response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body3 -ContentType "application/json"
Write-Host "Agent:" $response3.messages
```

## Testing Tips

1. **Use unique session IDs** for each test to avoid state conflicts
2. **Watch the uvicorn terminal** for debug output and errors
3. **Test both agents** to ensure routing works correctly
4. **Try various keywords** to test the routing logic

## Troubleshooting

### Issue: Empty response or wrong agent
- **Solution**: Check that you're using the correct keywords
- Appointment keywords: "appointment", "schedule", "book a visit", "book an appointment"

### Issue: 500 Internal Server Error
- **Solution**: Check uvicorn terminal for Python errors
- Restart server: `uvicorn api.main:app --reload`

### Issue: Connection refused
- **Solution**: Make sure server is running
- Start server: `cd backend; uvicorn api.main:app --reload`

## What Was Fixed

The orchestrator agent had an issue accessing the user message from the `InvocationContext`. 

**Problem**: Tried to access `ctx.latest_user_message` (doesn't exist)

**Solution**: Use `ctx.user_content.parts[0].text` to get the actual message

The fix is in: `backend/adk_app/orchestrator_agent.py`
