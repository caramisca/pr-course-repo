"""
Quick Test Runner for Lab 2
Automated testing script for all lab requirements.
"""

import subprocess
import sys
import time
import requests

def check_server(url, server_name):
    """Check if a server is running"""
    try:
        response = requests.get(url, timeout=2)
        print(f"✓ {server_name} is running on {url}")
        return True
    except:
        print(f"✗ {server_name} is NOT running on {url}")
        return False

def wait_for_enter(message="Press Enter to continue..."):
    """Wait for user input"""
    input(f"\n{message}")

def print_section(title):
    """Print a section header"""
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70 + "\n")

def main():
    print_section("LAB 2 - AUTOMATED TEST RUNNER")
    
    print("This script helps you test all Lab 2 requirements systematically.")
    print("\nBefore starting, make sure you have:")
    print("  - Lab 1 server ready: D:\\Labs PR\\Lab 1\\")
    print("  - Lab 2 server ready: D:\\Labs PR\\Lab-2\\")
    print("  - Python dependencies installed: pip install -r requirements.txt")
    
    wait_for_enter("Press Enter when ready to start...")
    
    # Test 1: Performance Comparison
    print_section("TEST 1: PERFORMANCE COMPARISON")
    print("This test compares single-threaded (Lab 1) vs multithreaded (Lab 2).")
    print("\nRequired setup:")
    print("  Terminal 1: cd \"D:\\Labs PR\\Lab 1\" && python server.py collection --delay 1")
    print("  Terminal 2: cd \"D:\\Labs PR\\Lab-2\" && python server.py collection --delay 1")
    
    wait_for_enter("Press Enter when both servers are running...")
    
    lab1_running = check_server("http://localhost:8081/", "Lab 1 (port 8081)")
    lab2_running = check_server("http://localhost:8080/", "Lab 2 (port 8080)")
    
    if lab1_running and lab2_running:
        print("\n✓ Both servers detected! Running performance test...")
        subprocess.run([sys.executable, "test_performance_comparison.py"])
        print("\n✓ TEST 1 COMPLETE - Take screenshot of the results above")
    else:
        print("\n✗ One or both servers not running. Please start them and try again.")
        return
    
    wait_for_enter()
    
    # Test 2: Race Condition
    print_section("TEST 2: RACE CONDITION DEMONSTRATION")
    print("This test shows lost updates when locks are disabled.")
    print("\nRequired setup:")
    print("  Stop Lab 2 server (Ctrl+C in Terminal 2)")
    print("  Restart WITHOUT locks: python server.py collection --no-lock --no-rate-limit")
    
    wait_for_enter("Press Enter when Lab 2 server is running without locks...")
    
    if check_server("http://localhost:8080/", "Lab 2 (no locks)"):
        print("\n✓ Server detected! Running race condition test...")
        subprocess.run([sys.executable, "test_counter_race.py"])
        print("\n✓ TEST 2A COMPLETE - Take screenshots:")
        print("  1. Terminal output above")
        print("  2. Browser: http://localhost:8080/Directory/images/")
        print("     (Should show LESS than 50 hits for README.html)")
    else:
        print("\n✗ Server not running. Please start it and try again.")
        return
    
    wait_for_enter()
    
    # Test 3: Fixed Counter
    print_section("TEST 3: FIXED COUNTER (WITH LOCKS)")
    print("This test shows correct counting when locks are enabled.")
    print("\nRequired setup:")
    print("  Stop Lab 2 server (Ctrl+C)")
    print("  Restart WITH locks: python server.py collection --no-rate-limit")
    
    wait_for_enter("Press Enter when Lab 2 server is running with locks...")
    
    if check_server("http://localhost:8080/", "Lab 2 (with locks)"):
        print("\n✓ Server detected! Running counter test...")
        subprocess.run([sys.executable, "test_counter_race.py"])
        print("\n✓ TEST 2B COMPLETE - Take screenshot:")
        print("  Browser: http://localhost:8080/Directory/images/")
        print("  (Should show EXACTLY 50 hits for README.html)")
    else:
        print("\n✗ Server not running. Please start it and try again.")
        return
    
    wait_for_enter()
    
    # Test 4: Rate Limiting
    print_section("TEST 4: RATE LIMITING")
    print("This test shows rate limiting in action (5 req/s per IP).")
    print("\nRequired setup:")
    print("  Stop Lab 2 server (Ctrl+C)")
    print("  Restart WITH rate limiting: python server.py collection")
    
    wait_for_enter("Press Enter when Lab 2 server is running with rate limiting...")
    
    if check_server("http://localhost:8080/", "Lab 2 (with rate limiting)"):
        print("\n✓ Server detected! Running rate limit test...")
        subprocess.run([sys.executable, "test_rate_limit.py", "single"])
        print("\n✓ TEST 3 COMPLETE - Take screenshots of:")
        print("  1. Spam client statistics (above)")
        print("  2. Legitimate client statistics (above)")
    else:
        print("\n✗ Server not running. Please start it and try again.")
        return
    
    # Summary
    print_section("ALL TESTS COMPLETE!")
    print("Summary of screenshots needed:")
    print("  ✓ Performance comparison (Lab 1 vs Lab 2)")
    print("  ✓ Race condition terminal output")
    print("  ✓ Race condition browser (< 50 hits)")
    print("  ✓ Fixed counter browser (= 50 hits)")
    print("  ✓ Rate limiting statistics")
    print("\nNext steps:")
    print("  1. Review all screenshots")
    print("  2. Replace README: copy README_NEW.md README.md")
    print("  3. Commit and push to repository")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
