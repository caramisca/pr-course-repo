# Distributed Key-Value Store - Startup Script
# This script builds and starts the distributed key-value store cluster

Write-Host "`n=========================================="
Write-Host "Starting Distributed Key-Value Store"
Write-Host "==========================================`n"

# Build and start containers
Write-Host "Building and starting containers..."
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ Error: Failed to start containers" -ForegroundColor Red
    Write-Host "Make sure Docker is running and try again.`n"
    exit 1
}

Write-Host "`nWaiting for services to start..."
Start-Sleep -Seconds 10

# Check leader health
Write-Host "`nChecking leader health..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "✓ Leader is healthy" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Leader is not responding" -ForegroundColor Red
}

# Check follower health
Write-Host "`nChecking follower health..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get -TimeoutSec 5
    Write-Host "✓ Follower 1 is healthy" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Follower 1 is not responding" -ForegroundColor Red
}

Write-Host "`n=========================================="
Write-Host "Cluster is ready!"
Write-Host "==========================================`n"

Write-Host "Leader: http://localhost:8000"
Write-Host "Followers: http://localhost:8001-8005`n"

Write-Host "Try these commands:"
Write-Host "  Write: curl -X POST http://localhost:8000/write -H 'Content-Type: application/json' -d '{`"key`":`"test`",`"value`":`"hello`"}'"
Write-Host "  Read:  curl http://localhost:8000/read?key=test`n"

Write-Host "Or run:"
Write-Host "  python example_usage.py"
Write-Host "  python integration_test.py"
Write-Host "  python performance_analysis.py`n"
