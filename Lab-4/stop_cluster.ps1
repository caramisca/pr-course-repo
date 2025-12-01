# Stop Distributed Key-Value Store Cluster

Write-Host "`n=========================================="
Write-Host "Stopping Distributed Key-Value Store"
Write-Host "==========================================`n"

docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Cluster stopped successfully`n" -ForegroundColor Green
} else {
    Write-Host "`n✗ Error stopping cluster`n" -ForegroundColor Red
}
