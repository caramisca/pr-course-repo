# PowerShell Script to Start Both Servers for Performance Comparison
# This script starts Lab 1 and Lab 2 servers in separate PowerShell windows

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "      PERFORMANCE COMPARISON TEST - SERVER STARTUP SCRIPT" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  1. Start Lab 1 server (port 8081) in a new window" -ForegroundColor Yellow
Write-Host "  2. Start Lab 2 server (port 8080) in a new window" -ForegroundColor Yellow
Write-Host "  3. Wait 3 seconds for servers to start" -ForegroundColor Yellow
Write-Host "  4. Run the performance comparison test" -ForegroundColor Yellow
Write-Host ""

# Check if venv exists
$venvPath = "D:\Labs PR\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "✗ Virtual environment not found at: $venvPath" -ForegroundColor Red
    Write-Host "Please create a virtual environment first." -ForegroundColor Red
    exit 1
}

# Check if Lab 1 collection exists
if (-not (Test-Path "D:\Labs PR\Lab 1\collection")) {
    Write-Host "✗ Lab 1 collection directory not found" -ForegroundColor Red
    exit 1
}

# Check if Lab 2 collection exists
if (-not (Test-Path "D:\Labs PR\Lab-2\collection")) {
    Write-Host "✗ Lab 2 collection directory not found" -ForegroundColor Red
    exit 1
}

Write-Host "Starting servers..." -ForegroundColor Yellow
Write-Host ""

# Start Lab 1 Server in new window
Write-Host "1. Starting Lab 1 (single-threaded) on port 8081..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {cd 'D:\Labs PR\Lab 1'; & '$venvPath'; Write-Host 'LAB 1 - SINGLE-THREADED SERVER' -ForegroundColor Green; python server.py collection --delay 1}"

Start-Sleep -Seconds 1

# Start Lab 2 Server in new window
Write-Host "2. Starting Lab 2 (multithreaded) on port 8080..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {cd 'D:\Labs PR\Lab-2'; & '$venvPath'; Write-Host 'LAB 2 - MULTITHREADED SERVER' -ForegroundColor Green; python server.py collection --delay 1}"

Write-Host ""
Write-Host "Waiting 3 seconds for servers to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Starting performance comparison test..." -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Run the test
& $venvPath
python test_performance_comparison.py

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Test complete! Check the results above." -ForegroundColor Green
Write-Host "Don't forget to close the server windows when done." -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
