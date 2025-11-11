# Race Condition Testing Script
# Automates testing with and without locks

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RACE CONDITION TEST AUTOMATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "This script will test the race condition in two scenarios:`n"
Write-Host "1. WITHOUT locks (race condition present)" -ForegroundColor Yellow
Write-Host "2. WITH locks (race condition fixed)`n" -ForegroundColor Green

# Test 1: WITHOUT LOCKS
Write-Host "`n========================================" -ForegroundColor Red
Write-Host "TEST 1: WITHOUT LOCKS (Race Condition)" -ForegroundColor Red
Write-Host "========================================`n" -ForegroundColor Red

Write-Host "Starting server WITHOUT locks..." -ForegroundColor Yellow
Write-Host "Command: python server.py collection --no-lock --no-rate-limit`n"

# Start server in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'D:\Labs PR\Lab-2'; python server.py collection --no-lock --no-rate-limit"

Write-Host "Waiting 3 seconds for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "`nRunning test..." -ForegroundColor Yellow
python test_counter_race.py

Write-Host "`n⚠️  CHECK THE BROWSER!" -ForegroundColor Yellow
Write-Host "Open: http://localhost:8080/Directory/images/" -ForegroundColor Cyan
Write-Host "The hit counter for README.html should be LESS than 50 (race condition!)`n"

Write-Host "Press Enter after checking the counter, then I'll stop the server and run Test 2..."
Read-Host

# Kill the server
Get-Process python | Where-Object {$_.MainWindowTitle -like "*server.py*"} | Stop-Process -Force

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "TEST 2: WITH LOCKS (Fixed)" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Starting server WITH locks..." -ForegroundColor Green
Write-Host "Command: python server.py collection --no-rate-limit`n"

# Start server in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'D:\Labs PR\Lab-2'; python server.py collection --no-rate-limit"

Write-Host "Waiting 3 seconds for server to start..." -ForegroundColor Green
Start-Sleep -Seconds 3

Write-Host "`nRunning test..." -ForegroundColor Green
python test_counter_race.py

Write-Host "`n✅ CHECK THE BROWSER!" -ForegroundColor Green
Write-Host "Open: http://localhost:8080/Directory/images/" -ForegroundColor Cyan
Write-Host "The hit counter for README.html should be EXACTLY 50 (fixed!)`n"

Write-Host "Press Enter to finish and close server..."
Read-Host

# Kill the server
Get-Process python | Where-Object {$_.MainWindowTitle -like "*server.py*"} | Stop-Process -Force

Write-Host "`n✅ Testing complete!" -ForegroundColor Green
Write-Host "You should see the difference in the hit counters between the two tests.`n"
