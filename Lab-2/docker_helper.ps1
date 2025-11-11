# PowerShell script to run Docker commands for Lab 2

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Lab 2 - Docker Helper Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

function Show-Menu {
    Write-Host "Select an option:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Setup:"
    Write-Host "  1. Install dependencies and generate sample files"
    Write-Host "  2. Build Docker images"
    Write-Host ""
    Write-Host "Run Server:"
    Write-Host "  3. Start server (normal mode)"
    Write-Host "  4. Start server (with 1s delay - port 8081)"
    Write-Host "  5. Start server (no locks - port 8082)"
    Write-Host "  6. Start all testing servers"
    Write-Host ""
    Write-Host "Client Operations:"
    Write-Host "  7. Download index.html"
    Write-Host "  8. Download logo.png"
    Write-Host "  9. Download lab_manual.pdf"
    Write-Host "  10. Interactive client mode"
    Write-Host ""
    Write-Host "Testing:"
    Write-Host "  11. Run performance test"
    Write-Host "  12. Run race condition test"
    Write-Host "  13. Run rate limiting test"
    Write-Host ""
    Write-Host "Management:"
    Write-Host "  14. View server logs"
    Write-Host "  15. Stop all containers"
    Write-Host "  16. Cleanup (stop and remove)"
    Write-Host "  17. Open browser to http://localhost:8080"
    Write-Host ""
    Write-Host "  0. Exit"
    Write-Host ""
}

while ($true) {
    Show-Menu
    $choice = Read-Host "Enter your choice"
    
    switch ($choice) {
        "1" {
            Write-Host "`nInstalling dependencies and generating files..." -ForegroundColor Green
            pip install -r requirements.txt
            python setup_files.py
        }
        "2" {
            Write-Host "`nBuilding Docker images..." -ForegroundColor Green
            docker-compose build
        }
        "3" {
            Write-Host "`nStarting server on port 8080..." -ForegroundColor Green
            Write-Host "Access at: http://localhost:8080" -ForegroundColor Yellow
            Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
            docker-compose up server
        }
        "4" {
            Write-Host "`nStarting delayed server on port 8081..." -ForegroundColor Green
            Write-Host "Access at: http://localhost:8081" -ForegroundColor Yellow
            docker-compose --profile testing up server_delayed
        }
        "5" {
            Write-Host "`nStarting server without locks on port 8082..." -ForegroundColor Green
            Write-Host "Access at: http://localhost:8082" -ForegroundColor Yellow
            docker-compose --profile testing up server_no_locks
        }
        "6" {
            Write-Host "`nStarting all testing servers..." -ForegroundColor Green
            Write-Host "Normal: http://localhost:8080" -ForegroundColor Yellow
            Write-Host "Delayed: http://localhost:8081" -ForegroundColor Yellow
            Write-Host "No Locks: http://localhost:8082" -ForegroundColor Yellow
            docker-compose --profile testing up -d
            Write-Host "`nAll servers started in background!" -ForegroundColor Green
        }
        "7" {
            Write-Host "`nDownloading index.html..." -ForegroundColor Green
            docker-compose run --rm client python client.py server 8080 /index.html ./downloads
        }
        "8" {
            Write-Host "`nDownloading logo.png..." -ForegroundColor Green
            docker-compose run --rm client python client.py server 8080 /images/logo.png ./downloads
        }
        "9" {
            Write-Host "`nDownloading lab_manual.pdf..." -ForegroundColor Green
            docker-compose run --rm client python client.py server 8080 /documents/lab_manual.pdf ./downloads
        }
        "10" {
            Write-Host "`nInteractive client mode" -ForegroundColor Green
            $host_input = Read-Host "Enter server (default: server)"
            $port_input = Read-Host "Enter port (default: 8080)"
            $path_input = Read-Host "Enter path (e.g., /index.html)"
            
            $host_val = if ($host_input) { $host_input } else { "server" }
            $port_val = if ($port_input) { $port_input } else { "8080" }
            
            if ($path_input) {
                docker-compose run --rm client python client.py $host_val $port_val $path_input ./downloads
            } else {
                Write-Host "Path is required!" -ForegroundColor Red
            }
        }
        "11" {
            Write-Host "`nRunning load test against a single server..." -ForegroundColor Green
            Write-Host "Tip: Start the delayed server (option 4) or any server you want to test first." -ForegroundColor Yellow
            $url = Read-Host "Enter target URL (default: http://localhost:8081/Directory/images/README.html)"
            if (-not $url) { $url = "http://localhost:8081/Directory/images/README.html" }
            $num = Read-Host "Number of concurrent requests (default: 20)"
            if (-not $num) { $num = 20 }
            $workers = Read-Host "Max worker threads (default: same as requests)"
            if (-not $workers) { python test_concurrent.py load $url $num }
            else { python test_concurrent.py load $url $num $workers }
        }
        "12" {
            Write-Host "`nRunning race condition test..." -ForegroundColor Green
            Write-Host "Make sure no-locks server is running (option 5 or 6)" -ForegroundColor Yellow
            Write-Host "Waiting 3 seconds..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
            python test_concurrent.py race
        }
        "13" {
            Write-Host "`nRunning rate limiting test..." -ForegroundColor Green
            Write-Host "Make sure normal server is running (option 3 or 6)" -ForegroundColor Yellow
            Write-Host "Waiting 3 seconds..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
            python test_rate_limit.py concurrent
        }
        "14" {
            Write-Host "`nViewing server logs..." -ForegroundColor Green
            Write-Host "Press Ctrl+C to exit logs" -ForegroundColor Yellow
            docker-compose logs -f server
        }
        "15" {
            Write-Host "`nStopping all containers..." -ForegroundColor Green
            docker-compose stop
            Write-Host "Containers stopped!" -ForegroundColor Green
        }
        "16" {
            Write-Host "`nCleaning up..." -ForegroundColor Green
            docker-compose down
            Write-Host "Cleanup complete!" -ForegroundColor Green
        }
        "17" {
            Write-Host "`nOpening browser..." -ForegroundColor Green
            Start-Process "http://localhost:8080"
        }
        "0" {
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
