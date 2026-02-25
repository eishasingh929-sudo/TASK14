$ErrorActionPreference = "Stop"

Write-Host "Starting UniGuru Admission Layer Demo..."
Write-Host "----------------------------------------"

# 1. Health Check
Write-Host "`n[1] Health Check (GET /health)"
Invoke-RestMethod -Uri "http://localhost:3000/health" -Method Get

# 2. Test Rejected: Empty Body
Write-Host "`n[2] Testing Rejected Request: Empty Body (expect 400)"
try {
    Invoke-RestMethod -Uri "http://localhost:3000/admit" -Method Post -Body '{}' -ContentType "application/json"
} catch {
    Write-Host " caught exeption: $($_.Exception.Message)"
    $params = $_.Exception.Response
    # Read the response stream if possible or just show status
    Write-Host " Status: $($params.StatusCode)"
}

# 3. Test Rejected: Unsafe SQL
Write-Host "`n[3] Testing Rejected Request: SQL Injection (expect 400)"
$sqlBody = @{ query = "DROP TABLE users;" } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "http://localhost:3000/admit" -Method Post -Body $sqlBody -ContentType "application/json"
} catch {
    Write-Host " caught exeption: $($_.Exception.Message)"
     Write-Host " Status: $($_.Exception.Response.StatusCode)"
}

# 4. Test Forwarding (Will likely fail 502 if upstream is down, which is expected behavior for this layer isolated)"
Write-Host "`n[4] Testing Forwarding (expect 502 if upstream not running)"
$validBody = @{ user = "demo"; action = "login" } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "http://localhost:3000/admit" -Method Post -Body $validBody -ContentType "application/json"
} catch {
     Write-Host " Status: $($_.Exception.Response.StatusCode)"
     # Verify it's 502
}

Write-Host "`nDemo Complete."
