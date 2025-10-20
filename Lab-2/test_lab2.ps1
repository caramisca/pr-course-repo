# Lab 2 Test Suite - PowerShell Script
# This script helps run all the tests for Lab 2

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Lab 2 - Multithreaded Server Tests" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Function to show menu
function Show-Menu {
    Write-Host "Select a test to run:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Start server (normal mode with 1s delay)"
    Write-Host "2. Start server (no locks - race condition demo)"
    Write-Host "3. Start server (normal mode - no delay)"
    Write-Host "4. Test concurrent requests (performance comparison)"
    Write-Host "5. Test race condition"
    Write-Host "6. Test rate limiting (single client)"
    Write-Host "7. Test rate limiting (concurrent clients)"
    Write-Host "8. Test rate limiting (burst traffic)"
    Write-Host "9. Exit"
    Write-Host ""
}

# Main loop
while ($true) {
    Show-Menu
    $choice = Read-Host "Enter your choice (1-9)"
    
    switch ($choice) {
        "1" {
            Write-Host "`nStarting server with 1s delay for testing..." -ForegroundColor Green
            Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
            Write-Host ""
            python server.py "../Lab 1/collection" --delay 1
        }
        "2" {
            Write-Host "`nStarting server WITHOUT locks (race condition demo)..." -ForegroundColor Green
            Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
            Write-Host ""
            python server.py "../Lab 1/collection" --no-lock
        }
        "3" {
            Write-Host "`nStarting server (normal mode)..." -ForegroundColor Green
            Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
            Write-Host ""
            python server.py "../Lab 1/collection"
        }
        "4" {
            Write-Host "`nTesting concurrent requests..." -ForegroundColor Green
            Write-Host "Make sure server is running with --delay 1" -ForegroundColor Yellow
            Write-Host ""
            python test_concurrent.py compare
        }
        "5" {
            Write-Host "`nTesting race condition..." -ForegroundColor Green
            Write-Host "Make sure server is running with --no-lock" -ForegroundColor Yellow
            Write-Host ""
            python test_concurrent.py race
        }
        "6" {
            Write-Host "`nTesting rate limiting (single client)..." -ForegroundColor Green
            Write-Host "Make sure server is running (normal mode)" -ForegroundColor Yellow
            Write-Host ""
            python test_rate_limit.py single
        }
        "7" {
            Write-Host "`nTesting rate limiting (concurrent clients)..." -ForegroundColor Green
            Write-Host "Make sure server is running (normal mode)" -ForegroundColor Yellow
            Write-Host ""
            python test_rate_limit.py concurrent
        }
        "8" {
            Write-Host "`nTesting rate limiting (burst traffic)..." -ForegroundColor Green
            Write-Host "Make sure server is running (normal mode)" -ForegroundColor Yellow
            Write-Host ""
            python test_rate_limit.py burst
        }
        "9" {
            Write-Host "`nExiting..." -ForegroundColor Green
            exit
        }
        default {
            Write-Host "`nInvalid choice. Please try again." -ForegroundColor Red
        }
    }
    
    Write-Host "`n================================" -ForegroundColor Cyan
    Write-Host "Press Enter to continue..." -ForegroundColor Yellow
    Read-Host
    Clear-Host
}
