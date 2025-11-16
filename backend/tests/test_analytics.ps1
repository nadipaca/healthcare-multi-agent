# Test Analytics System
# This script generates test interactions and views analytics

$baseUrl = "http://localhost:8000"

Write-Host "`n=== Testing Analytics System ===" -ForegroundColor Cyan

# Create test sessions with different agents
$sessions = @(
    @{ id = "analytics-test-1"; messages = @("I have a headache and fever", "Schedule appointment for tomorrow", "Is this covered by insurance?") },
    @{ id = "analytics-test-2"; messages = @("Book appointment with Dr. Smith", "What time slots are available?") },
    @{ id = "analytics-test-3"; messages = @("Check my insurance eligibility", "What's my copay for MRI?") }
)

Write-Host "`nGenerating test interactions..." -ForegroundColor Yellow

foreach ($session in $sessions) {
    Write-Host "`n  Session: $($session.id)" -ForegroundColor Gray
    
    foreach ($message in $session.messages) {
        try {
            $body = @{
                session_id = $session.id
                message = $message
            } | ConvertTo-Json

            $response = Invoke-RestMethod `
                -Uri "$baseUrl/api/chat" `
                -Method Post `
                -Body $body `
                -ContentType "application/json"
            
            Write-Host "    ✓ '$message'" -ForegroundColor Green
            Start-Sleep -Seconds 1
        }
        catch {
            Write-Host "    ✗ '$message' - Error" -ForegroundColor Red
        }
    }
}

# Add some ratings
Write-Host "`nAdding user ratings..." -ForegroundColor Yellow
try {
    $ratingBody = @{
        session_id = "analytics-test-1"
        rating = 5
    } | ConvertTo-Json

    Invoke-RestMethod `
        -Uri "$baseUrl/api/feedback/rating" `
        -Method Post `
        -Body $ratingBody `
        -ContentType "application/json" | Out-Null
    
    Write-Host "  ✓ 5-star rating added" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Failed to add rating" -ForegroundColor Red
}

# View dashboard metrics
Write-Host "`n=== Dashboard Metrics ===" -ForegroundColor Cyan
try {
    $dashboard = Invoke-RestMethod `
        -Uri "$baseUrl/api/analytics/dashboard?hours=1" `
        -Method Get
    
    Write-Host "`nOverview:" -ForegroundColor White
    Write-Host "  Total Interactions: $($dashboard.overview.total_interactions)"
    Write-Host "  Active Sessions: $($dashboard.overview.active_sessions)"
    Write-Host "  HITL Flags: $($dashboard.overview.hitl_flags)"
    
    Write-Host "`nAgent Usage:" -ForegroundColor White
    foreach ($agent in $dashboard.agent_usage.PSObject.Properties) {
        Write-Host "  $($agent.Name): $($agent.Value) calls"
    }
    
    Write-Host "`nAgent Performance:" -ForegroundColor White
    foreach ($agent in $dashboard.agent_performance.PSObject.Properties) {
        $perf = $agent.Value
        Write-Host "  $($agent.Name):"
        Write-Host "    Avg Duration: $($perf.avg_duration_ms) ms"
        Write-Host "    Avg Rating: $($perf.avg_rating)"
        Write-Host "    HITL Rate: $($perf.hitl_rate)%"
    }
    
    Write-Host "`nTop Sessions:" -ForegroundColor White
    foreach ($session in $dashboard.top_sessions) {
        Write-Host "  $($session.session_id): $($session.total_interactions) interactions, $($session.agents_used) agents"
    }
}
catch {
    Write-Host "Failed to get dashboard metrics" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Gray
}

# View specific session details
Write-Host "`n=== Session Details ===" -ForegroundColor Cyan
try {
    $sessionDetails = Invoke-RestMethod `
        -Uri "$baseUrl/api/analytics/session/analytics-test-1" `
        -Method Get
    
    Write-Host "Session: analytics-test-1" -ForegroundColor White
    Write-Host "  Total Interactions: $($sessionDetails.total_interactions)"
    Write-Host "  Unique Agents: $($sessionDetails.unique_agents)"
    Write-Host "  HITL Flags: $($sessionDetails.hitl_flags)"
    Write-Host "  Average Rating: $($sessionDetails.average_rating)"
    Write-Host "  Duration: $($sessionDetails.duration_minutes) minutes"
}
catch {
    Write-Host "Failed to get session details" -ForegroundColor Red
}

Write-Host "`n=== View Dashboard in Browser ===" -ForegroundColor Cyan
Write-Host "Open: backend/dashboard.html in your browser" -ForegroundColor Yellow
Write-Host "Dashboard auto-refreshes every 30 seconds" -ForegroundColor Gray

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
