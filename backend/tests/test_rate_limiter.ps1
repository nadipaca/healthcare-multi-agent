# Test Rate Limiter
# This script tests the rate limiting functionality

$baseUrl = "http://localhost:8000"
$sessionId = "test-rate-limit-" + (Get-Random)

Write-Host "`n=== Testing Rate Limiter ===" -ForegroundColor Cyan
Write-Host "Session ID: $sessionId`n" -ForegroundColor Gray

# Make 25 requests rapidly (limit is 20/min)
Write-Host "Making 25 rapid requests (limit: 20/min)..." -ForegroundColor Yellow

for ($i = 1; $i -le 25; $i++) {
    try {
        $body = @{
            session_id = $sessionId
            message = "Test message $i"
        } | ConvertTo-Json

        $response = Invoke-RestMethod `
            -Uri "$baseUrl/api/chat" `
            -Method Post `
            -Body $body `
            -ContentType "application/json"
        
        Write-Host "✓ Request $i : Success" -ForegroundColor Green
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq 429) {
            Write-Host "✗ Request $i : Rate Limited (429 Too Many Requests)" -ForegroundColor Red
            
            # Try to extract retry_after from error
            $errorBody = $_.ErrorDetails.Message | ConvertFrom-Json
            if ($errorBody.retry_after) {
                Write-Host "   Retry after: $($errorBody.retry_after) seconds" -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "✗ Request $i : Error $statusCode" -ForegroundColor Red
        }
    }
    
    # Small delay to show progress
    Start-Sleep -Milliseconds 50
}

Write-Host "`n=== Checking Rate Limit Status ===" -ForegroundColor Cyan
try {
    $rateLimitStatus = Invoke-RestMethod `
        -Uri "$baseUrl/api/analytics/rate-limits/$sessionId" `
        -Method Get
    
    Write-Host "Remaining requests (per minute): $($rateLimitStatus.remaining_per_minute)" -ForegroundColor $(if ($rateLimitStatus.remaining_per_minute -gt 0) { "Green" } else { "Red" })
    Write-Host "Remaining requests (per hour): $($rateLimitStatus.remaining_per_hour)" -ForegroundColor $(if ($rateLimitStatus.remaining_per_hour -gt 0) { "Green" } else { "Red" })
}
catch {
    Write-Host "Failed to get rate limit status" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
