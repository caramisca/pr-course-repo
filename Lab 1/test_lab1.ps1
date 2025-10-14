# Testing Script for Lab 1

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  Lab 1: HTTP File Server - Automated Testing Script" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$pythonPath = "D:/Labs PR/.venv/Scripts/python.exe"
$serverPath = "d:\Labs PR\Lab 1\server.py"
$clientPath = "d:\Labs PR\Lab 1\client.py"
$serverDir = "collection"
$downloadDir = "downloads"
$serverHost = "localhost"
$serverPort = 8080

# Change to Lab 1 directory
Set-Location "d:\Labs PR\Lab 1"

Write-Host "[1/8] Checking prerequisites..." -ForegroundColor Yellow
if (Test-Path $pythonPath) {
    Write-Host "  [OK] Python found: $pythonPath" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Python not found at: $pythonPath" -ForegroundColor Red
    exit 1
}

if (Test-Path $serverPath) {
    Write-Host "  [OK] Server script found" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Server script not found" -ForegroundColor Red
    exit 1
}

if (Test-Path $clientPath) {
    Write-Host "  [OK] Client script found" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Client script not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/8] Cleaning up old downloads..." -ForegroundColor Yellow
if (Test-Path $downloadDir) {
    Remove-Item "$downloadDir\*" -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Downloads directory cleaned" -ForegroundColor Green
} else {
    New-Item -ItemType Directory -Path $downloadDir | Out-Null
    Write-Host "  [OK] Downloads directory created" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/8] Starting HTTP server..." -ForegroundColor Yellow
$serverJob = Start-Job -ScriptBlock {
    param($pythonPath, $serverPath, $serverDir)
    Set-Location "d:\Labs PR\Lab 1"
    & $pythonPath $serverPath $serverDir
} -ArgumentList $pythonPath, $serverPath, $serverDir

Start-Sleep -Seconds 3

if ($serverJob.State -eq "Running") {
    Write-Host "  [OK] Server started successfully" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Server failed to start" -ForegroundColor Red
    $serverJob | Remove-Job -Force
    exit 1
}

Write-Host ""
Write-Host "[4/8] Testing HTML file request..." -ForegroundColor Yellow
$result = & $pythonPath $clientPath $serverHost $serverPort "/index.html" $downloadDir 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] HTML file request successful" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] HTML file request failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "[5/8] Testing PNG image download..." -ForegroundColor Yellow
$result = & $pythonPath $clientPath $serverHost $serverPort "/network_diagram.png" $downloadDir 2>&1
if ($LASTEXITCODE -eq 0 -and (Test-Path "$downloadDir\network_diagram.png")) {
    $fileSize = (Get-Item "$downloadDir\network_diagram.png").Length
    Write-Host "  [OK] PNG downloaded successfully ($fileSize bytes)" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] PNG download failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "[6/8] Testing PDF file download..." -ForegroundColor Yellow
$result = & $pythonPath $clientPath $serverHost $serverPort "/Books/Computer_Networking_Kurose_Ross.pdf" $downloadDir 2>&1
if ($LASTEXITCODE -eq 0 -and (Test-Path "$downloadDir\Computer_Networking_Kurose_Ross.pdf")) {
    $fileSize = (Get-Item "$downloadDir\Computer_Networking_Kurose_Ross.pdf").Length
    Write-Host "  [OK] PDF downloaded successfully ($fileSize bytes)" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] PDF download failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "[7/8] Testing 404 error handling..." -ForegroundColor Yellow
$result = & $pythonPath $clientPath $serverHost $serverPort "/nonexistent.html" $downloadDir 2>&1
if ($result -match "404") {
    Write-Host "  [OK] 404 error handled correctly" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] 404 error handling failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "[8/8] Testing directory listing..." -ForegroundColor Yellow
$result = & $pythonPath $clientPath $serverHost $serverPort "/Books/" $downloadDir 2>&1
if ($result -match "Directory Listing") {
    Write-Host "  [OK] Directory listing generated successfully" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Directory listing failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  Stopping server..." -ForegroundColor Yellow
$serverJob | Stop-Job
$serverJob | Remove-Job
Write-Host "  [OK] Server stopped" -ForegroundColor Green

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Downloaded files:" -ForegroundColor Yellow
Get-ChildItem $downloadDir | ForEach-Object {
    $size = $_.Length
    Write-Host "  - $($_.Name) - $size bytes" -ForegroundColor White
}

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  All tests completed!" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review the full report in README.md" -ForegroundColor White
Write-Host "  2. Install Docker using DOCKER_SETUP.md" -ForegroundColor White
Write-Host "  3. Test with Docker Compose" -ForegroundColor White
Write-Host "  4. Connect with a friend for bonus point" -ForegroundColor White
Write-Host "  5. Prepare for presentation" -ForegroundColor White
Write-Host ""
