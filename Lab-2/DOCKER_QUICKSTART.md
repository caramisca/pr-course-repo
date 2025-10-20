# Lab 2 - Complete Docker Setup

## 🚀 Complete Setup from Scratch

Follow these steps to get Lab 2 running with Docker:

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Generate Sample Files
```powershell
python setup_files.py
```

This creates:
- **HTML files**: index.html, about.html, and README files in subdirectories
- **PNG images**: logo.png, banner.png, icon.png
- **PDF documents**: lab_manual.pdf, concurrency_paper.pdf, threading_guide.pdf, rate_limiting.pdf

### Step 3: Build Docker Images
```powershell
docker-compose build
```

### Step 4: Start the Server
```powershell
docker-compose up server
```

Visit: **http://localhost:8080**

---

## 🎯 Using the Docker Helper Script

For ease of use, run the interactive helper script:

```powershell
.\docker_helper.ps1
```

This provides a menu with all options:
- Setup and build
- Start servers (normal, delayed, no-locks)
- Run client commands
- Execute tests
- View logs and manage containers

---

## 📦 Docker Compose Services

### 1. Normal Server (port 8080)
```powershell
docker-compose up server
```

### 2. Delayed Server (port 8081) - For concurrency testing
```powershell
docker-compose --profile testing up server_delayed
```

### 3. No-Locks Server (port 8082) - For race condition demo
```powershell
docker-compose --profile testing up server_no_locks
```

### 4. All Testing Servers
```powershell
docker-compose --profile testing up -d
```

---

## 💾 Using the HTTP Client

### Download Files

```powershell
# Download HTML
docker-compose run --rm client python client.py server 8080 /index.html ./downloads

# Download PNG
docker-compose run --rm client python client.py server 8080 /images/logo.png ./downloads

# Download PDF
docker-compose run --rm client python client.py server 8080 /documents/lab_manual.pdf ./downloads
```

Files are saved to the `downloads/` directory.

---

## 🧪 Running Tests with Docker

### Test 1: Performance (Concurrent Requests)

```powershell
# Start delayed server
docker-compose --profile testing up -d server_delayed

# Run test (from host)
python test_concurrent.py compare
```

**Expected:** 10 requests with 1s delay complete in ~1-2s

### Test 2: Race Condition

```powershell
# Start server without locks
docker-compose --profile testing up -d server_no_locks

# Run test
python test_concurrent.py race

# Check results at http://localhost:8082
```

**Expected:** Hit count < actual requests (race condition demo)

### Test 3: Rate Limiting

```powershell
# Start normal server
docker-compose up -d server

# Run test
python test_rate_limit.py concurrent
```

**Expected:** Spam client blocked, legitimate client succeeds

---

## 🗂️ Collection Directory Structure

After running `setup_files.py`:

```
collection/
├── index.html                  # Main page
├── about.html                  # About page
├── images/
│   ├── logo.png               # Lab 2 logo (800x600)
│   ├── banner.png             # Welcome banner (1200x300)
│   ├── icon.png               # HTTP icon (256x256)
│   └── README.html            # Image gallery page
├── documents/
│   ├── lab_manual.pdf         # Lab instructions
│   ├── concurrency_paper.pdf  # Research paper
│   └── README.html            # Documents index
└── Books/
    ├── threading_guide.pdf    # Threading book
    ├── rate_limiting.pdf      # Rate limiting guide
    └── README.html            # Books catalog
```

---

## 🔄 Complete Testing Workflow

```powershell
# 1. Setup (first time only)
pip install -r requirements.txt
python setup_files.py
docker-compose build

# 2. Start all testing servers
docker-compose --profile testing up -d

# 3. Test in browser
# http://localhost:8080 - Normal server
# http://localhost:8081 - Delayed server
# http://localhost:8082 - No-locks server

# 4. Test client downloads
docker-compose run --rm client python client.py server 8080 /index.html ./downloads
docker-compose run --rm client python client.py server 8080 /images/logo.png ./downloads
docker-compose run --rm client python client.py server 8080 /documents/lab_manual.pdf ./downloads

# 5. Check downloads
ls downloads/

# 6. Run performance test
python test_concurrent.py compare

# 7. Run race condition test
python test_concurrent.py race

# 8. Run rate limiting test
python test_rate_limit.py concurrent

# 9. View logs
docker-compose logs server

# 10. Cleanup
docker-compose down
```

---

## 📊 What to Include in Your Report

### Screenshots to Capture:

1. **Docker setup:**
   - `docker-compose ps` showing running containers
   - Browser showing http://localhost:8080

2. **Client downloads:**
   - Terminal showing client downloading files
   - `downloads/` directory with downloaded files

3. **Performance test:**
   - Test output showing 10 requests in ~1-2s
   - Server logs showing multiple threads

4. **Race condition:**
   - Directory listing without locks (incorrect count)
   - Directory listing with locks (correct count)

5. **Rate limiting:**
   - Test output showing spam blocked, legit succeeds
   - Server logs showing HTTP 429 responses

---

## 🛠️ Troubleshooting

### Issue: "Port already in use"
```powershell
# Check what's using the port
netstat -ano | findstr :8080

# Stop conflicting service or change port in docker-compose.yml
```

### Issue: "Setup files not found"
```powershell
# Run setup script
python setup_files.py

# Verify files created
ls collection/
```

### Issue: "Cannot download files"
```powershell
# Make sure server is running
docker-compose ps

# Start server if not running
docker-compose up -d server

# Try client again
docker-compose run --rm client python client.py server 8080 /index.html ./downloads
```

### Issue: "Tests fail to connect"
```powershell
# Check server is running
docker-compose ps

# Check server logs
docker-compose logs server

# Restart server
docker-compose restart server
```

---

## 🎓 Learning Points

Using Docker for this lab demonstrates:
- **Containerization** - Isolated, reproducible environment
- **Service orchestration** - Multiple server configurations
- **Volume mounting** - Shared data between host and container
- **Networking** - Container-to-container communication
- **Development workflow** - Easy testing and deployment

---

## ✅ Completion Checklist

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Sample files generated (`python setup_files.py`)
- [ ] Docker images built (`docker-compose build`)
- [ ] Server starts successfully (`docker-compose up server`)
- [ ] Can access http://localhost:8080 in browser
- [ ] Client can download HTML files
- [ ] Client can download PNG images
- [ ] Client can download PDF documents
- [ ] Performance test runs successfully
- [ ] Race condition visible without locks
- [ ] Race condition fixed with locks
- [ ] Rate limiting works correctly
- [ ] All screenshots captured for report

---

## 🎉 You're Ready!

Your Docker setup is complete when:
- ✅ All services start without errors
- ✅ Browser shows the Lab 2 homepage
- ✅ Client can download all file types
- ✅ All tests pass
- ✅ Screenshots captured for report

**Excellent work on Docker-izing Lab 2!** 🐳🚀
