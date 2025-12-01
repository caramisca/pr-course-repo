# Run All Tests for Distributed Key-Value Store

Write-Host "`n=========================================="
Write-Host "Running All Tests"
Write-Host "==========================================`n"

# Check if cluster is running
Write-Host "Checking if cluster is running..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Cluster is running`n" -ForegroundColor Green
} catch {
    Write-Host "✗ Cluster is not running" -ForegroundColor Red
    Write-Host "Starting cluster...`n"
    .\start_cluster.ps1
    Start-Sleep -Seconds 5
}

# Run setup check
Write-Host "`n=========================================="
Write-Host "1. Setup Check"
Write-Host "==========================================`n"
python setup_check.py

# Run example usage
Write-Host "`n=========================================="
Write-Host "2. Example Usage"
Write-Host "==========================================`n"
python example_usage.py

# Run integration tests
Write-Host "`n=========================================="
Write-Host "3. Integration Tests"
Write-Host "==========================================`n"
python integration_test.py

Write-Host "`n=========================================="
Write-Host "All Tests Completed"
Write-Host "==========================================`n"

Write-Host "To run performance analysis (takes 5-10 minutes):"
Write-Host "  python performance_analysis.py`n"
