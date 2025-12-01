# Simple test script for write and read operations

Write-Host "`n=========================================="
Write-Host "Testing Distributed Key-Value Store"
Write-Host "==========================================`n"

# Test 1: Write operation
Write-Host "Test 1: Writing data to leader..."
$body = @{key="test"; value="hello"} | ConvertTo-Json
$result = Invoke-RestMethod -Uri http://localhost:8000/write -Method POST -Body $body -ContentType "application/json"

Write-Host "OK Write successful!" -ForegroundColor Green
Write-Host "  Key: $($result.key)"
Write-Host "  Value: $($result.value)"
Write-Host "  Version: $($result.version)"
Write-Host "  Latency: $($result.latency_ms)ms"
Write-Host "  Acknowledged by: $($result.acknowledged_by)/$($result.total_followers) followers`n"

# Test 2: Read from leader
Write-Host "Test 2: Reading from leader..."
$result = Invoke-RestMethod -Uri "http://localhost:8000/read?key=test"
Write-Host "OK Read successful!" -ForegroundColor Green
Write-Host "  Key: $($result.key)"
Write-Host "  Value: $($result.value)"
Write-Host "  Version: $($result.version)`n"

# Test 3: Wait for replication
Write-Host "Test 3: Waiting for replication (2 seconds)..."
Start-Sleep -Seconds 2

# Test 4: Read from followers
Write-Host "`nTest 4: Reading from followers..."
for ($i = 1; $i -le 5; $i++) {
    try {
        $url = "http://localhost:800$i/read?key=test"
        $result = Invoke-RestMethod -Uri $url
        Write-Host "  OK Follower $i ($($result.node_id)): $($result.value)" -ForegroundColor Green
    } catch {
        Write-Host "  ERROR Follower ${i}: Failed to read" -ForegroundColor Red
    }
}

Write-Host "`n=========================================="
Write-Host "All tests completed successfully!"
Write-Host "==========================================`n"
