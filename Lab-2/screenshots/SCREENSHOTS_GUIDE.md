# Screenshots Needed for README.md

This file lists all the screenshots referenced in the README.md that you need to capture and place in the `screenshots/` folder.

## Required Screenshots

### 1. Project Structure
**Filename:** `project_structure.png`  
**Description:** File explorer showing the Lab-2 directory structure  
**How to capture:** Open File Explorer, navigate to Lab-2 folder, take screenshot

---

### 2. Docker Files
**Filename:** `dockerfile.png`  
**Description:** The Dockerfile content  
**How to capture:** Open Dockerfile in editor, take screenshot

**Filename:** `docker_compose.png`  
**Description:** The docker-compose.yml content  
**How to capture:** Open docker-compose.yml in editor, take screenshot

---

### 3. Performance Tests

**Filename:** `time_single.png`  
**Description:** Terminal showing single-threaded server performance (10 requests taking ~10 seconds)  
**How to capture:**
```bash
# This would be from Lab 1 single-threaded server or simulated
# Show terminal output with timing around 10 seconds for 10 requests
```

**Filename:** `time_multi.png`  
**Description:** Terminal showing multithreaded server performance (10 requests taking ~1.2 seconds)  
**How to capture:**
```bash
python server.py collection --delay 1
# In another terminal:
python test_concurrent.py compare
# Screenshot the output showing ~1.2s total time and 8x speedup
```

---

### 4. Race Condition Demonstration

**Filename:** `race_condition_no_lock.png`  
**Description:** Browser showing directory listing with hit counter LESS than 50 (e.g., 34 hits)  
**How to capture:**
```bash
# Terminal 1:
python server.py collection --no-lock --no-rate-limit

# Terminal 2:
python test_counter_race.py

# Browser:
# Open http://localhost:8080/Directory/images/
# Take screenshot showing README.html with ~34 hits (not 50)
```

**Filename:** `terminal_race_condition.png`  
**Description:** Terminal showing 50 successful requests made  
**How to capture:**
```bash
# Screenshot the terminal running test_counter_race.py
# Should show "✓ Request 1: Success (200)" ... "✓ Request 50: Success (200)"
# And "Successful requests: 50"
```

**Filename:** `race_condition_fixed.png`  
**Description:** Browser showing directory listing with hit counter EXACTLY 50  
**How to capture:**
```bash
# Terminal 1 (restart server WITH locks):
python server.py collection --no-rate-limit

# Terminal 2:
python test_counter_race.py

# Browser (refresh):
# Open http://localhost:8080/Directory/images/
# Take screenshot showing README.html with exactly 50 hits
```

---

### 5. Directory Listing

**Filename:** `directory_listing.png`  
**Description:** Browser showing hacker terminal-style directory listing with hit counters  
**How to capture:**
```bash
# Open http://localhost:8080/Directory/images/
# Take screenshot showing:
# - Black background (#000)
# - Green text (#0f0)
# - Terminal prompt
# - File listings with [FILE] prefixes
# - Hit counters (► 50, etc.)
```

---

### 6. Rate Limiting

**Filename:** `rate_limit_429.png`  
**Description:** Browser showing 429 "Too Many Requests" error page  
**How to capture:**
```bash
# In terminal:
python -c "import requests; [requests.get('http://localhost:8080/Directory/images/README.html') for _ in range(10)]"
# Quickly refresh browser several times to trigger 429
# Take screenshot of the error page
```

**Filename:** `spam_client.png`  
**Description:** Terminal showing spam client test results (50% blocked)  
**How to capture:**
```bash
python test_rate_limit.py single
# When prompted, choose Test 2 (above rate limit)
# Screenshot showing:
# - Successful: 25 (50%)
# - Blocked: 25 (50%)
# - Throughput: 2.5 req/s
```

**Filename:** `legit_client.png`  
**Description:** Terminal showing legitimate client test results (0% blocked)  
**How to capture:**
```bash
python test_rate_limit.py single
# When prompted, choose Test 1 (at rate limit)
# Screenshot showing:
# - Successful: 25 (100%)
# - Blocked: 0 (0%)
# - Throughput: 4.0 req/s
```

**Filename:** `concurrent_rate_limit.png`  
**Description:** Terminal showing concurrent clients test (spam + legitimate)  
**How to capture:**
```bash
python test_rate_limit.py concurrent
# Screenshot showing results for both clients
```

---

### 7. UI Design

**Filename:** `glassmorphism.png`  
**Description:** Browser showing index.html or about.html with glassmorphism design  
**How to capture:**
```bash
# Open http://localhost:8080/index.html
# Take screenshot showing:
# - Blurred translucent containers
# - Background image
# - Glass-style cards
# - Smooth animations
```

**Filename:** `hacker_terminal.png`  
**Description:** Another view of directory listing emphasizing terminal aesthetic  
**How to capture:**
```bash
# Open http://localhost:8080/Directory/
# Take screenshot showing terminal prompt, ls command, file listings
```

---

## Quick Screenshot Capture Commands

### Complete Test Sequence:

```bash
# 1. Start server WITHOUT locks
python server.py collection --no-lock --no-rate-limit

# 2. Run race condition test
python test_counter_race.py
# → Screenshot terminal output (terminal_race_condition.png)
# → Screenshot browser with ~34 hits (race_condition_no_lock.png)

# 3. Restart server WITH locks
# Stop server (Ctrl+C), then:
python server.py collection --no-rate-limit

# 4. Run race condition test again
python test_counter_race.py
# → Screenshot browser with exactly 50 hits (race_condition_fixed.png)

# 5. Test concurrent performance
python server.py collection --delay 1
# In another terminal:
python test_concurrent.py compare
# → Screenshot terminal output (time_multi.png)

# 6. Test rate limiting
python server.py collection  # with rate limiting enabled
python test_rate_limit.py single
# → Screenshot spam client results (spam_client.png)
# → Screenshot legit client results (legit_client.png)

python test_rate_limit.py concurrent
# → Screenshot concurrent results (concurrent_rate_limit.png)

# 7. Capture UI screenshots
# → Open http://localhost:8080/index.html (glassmorphism.png)
# → Open http://localhost:8080/Directory/images/ (directory_listing.png)
# → Open http://localhost:8080/Directory/ (hacker_terminal.png)

# 8. Capture Docker screenshots
# → Open Dockerfile in editor (dockerfile.png)
# → Open docker-compose.yml in editor (docker_compose.png)
```

---

## Screenshot Checklist

- [ ] project_structure.png
- [ ] dockerfile.png
- [ ] docker_compose.png
- [ ] time_single.png (optional - can show Lab 1 results or explain in text)
- [ ] time_multi.png
- [ ] race_condition_no_lock.png
- [ ] terminal_race_condition.png
- [ ] race_condition_fixed.png
- [ ] directory_listing.png
- [ ] rate_limit_429.png
- [ ] spam_client.png
- [ ] legit_client.png
- [ ] concurrent_rate_limit.png
- [ ] glassmorphism.png
- [ ] hacker_terminal.png

**Total: 15 screenshots**

---

## Tips

1. **Use consistent window size** - Use the same browser window size for all screenshots
2. **Clear terminal** - Use `cls` or `clear` before running commands for clean screenshots
3. **Font size** - Make sure terminal font is readable in screenshots
4. **Crop appropriately** - Remove unnecessary parts but keep context
5. **File format** - Use PNG for best quality
6. **Naming** - Follow exact filenames as listed above
7. **Dimensions** - Reasonable resolution (800-1200px width is good)

---

## Alternative Screenshot Names

If you prefer different filenames, update these references in README.md:
- All screenshot references are in format: `./screenshots/filename.png`
- Use Find & Replace in README.md to change filenames if needed
