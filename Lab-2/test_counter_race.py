"""
Counter Race Condition Test - Lab 2
Demonstrates the race condition in request counter with and without locks.
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import re


def check_server(url):
    """Check if server is running"""
    try:
        response = requests.get(url, timeout=2)
        return True
    except:
        return False


def get_counter_value(base_url, file_path):
    """
    Get the current counter value for a file by scraping the directory listing
    
    Args:
        base_url: Base URL of the server
        file_path: Path like "Directory/images/README.html"
        
    Returns:
        Counter value as integer, or None if not found
    """
    try:
        # Get the directory listing page
        dir_path = '/'.join(file_path.split('/')[:-1])
        filename = file_path.split('/')[-1]
        
        response = requests.get(f"{base_url}/{dir_path}/", timeout=5)
        if response.status_code != 200:
            return None
        
        html = response.text
        
        # Find the row for this file - pattern: <td class="file"><a href="...">README.html</a></td><td class="hits">42</td>
        pattern = rf'<td class="file"><a[^>]*>{re.escape(filename)}</a></td><td class="hits">(\d+)</td>'
        match = re.search(pattern, html)
        
        if match:
            return int(match.group(1))
        return None
        
    except Exception as e:
        print(f"Error getting counter: {e}")
        return None


def make_request(url, request_id):
    """Make a single HTTP request"""
    try:
        response = requests.get(url, timeout=10)
        return (request_id, response.status_code, response.headers.get('Content-Type', 'unknown'))
    except Exception as e:
        return (request_id, f"ERROR: {e}", None)


def test_counter_race(url, num_requests=50, max_workers=20):
    """
    Test the request counter with concurrent requests
    
    Args:
        url: URL to test
        num_requests: Number of concurrent requests
        max_workers: Number of concurrent threads
    """
    print(f"\n{'='*70}")
    print(f"COUNTER RACE CONDITION TEST")
    print(f"{'='*70}")
    print(f"\nMaking {num_requests} concurrent requests to: {url}")
    print(f"Using {max_workers} worker threads")
    print(f"\n{'='*70}\n")
    
    successful_requests = 0
    failed_requests = 0
    blocked_requests = 0
    
    start_time = time.time()
    
    # Make concurrent requests
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(make_request, url, i): i 
            for i in range(num_requests)
        }
        
        # Collect results
        for future in as_completed(futures):
            request_id, status, content_type = future.result()
            
            if status == 200:
                successful_requests += 1
                print(f"✓ Request {request_id:3d}: Success (200)")
            elif status == 429:
                blocked_requests += 1
                print(f"⊘ Request {request_id:3d}: Rate Limited (429)")
            else:
                failed_requests += 1
                print(f"✗ Request {request_id:3d}: {status}")
    
    end_time = time.time()
    
    print(f"\n{'='*70}")
    print(f"TEST RESULTS")
    print(f"{'='*70}")
    print(f"Total requests sent:      {num_requests}")
    print(f"Successful (200):         {successful_requests}")
    print(f"Rate limited (429):       {blocked_requests}")
    print(f"Failed/errors:            {failed_requests}")
    print(f"Total time:               {end_time - start_time:.3f}s")
    print(f"{'='*70}\n")
    
    return successful_requests


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("REQUEST COUNTER RACE CONDITION DEMONSTRATION")
    print("="*70)
    print("\nThis test demonstrates the race condition in the request counter.")
    print("\nYou should run this test twice:")
    print("\n1. WITH race condition (no locks):")
    print("   python server.py collection --no-lock --no-rate-limit")
    print("\n2. WITHOUT race condition (with locks):")
    print("   python server.py collection --no-rate-limit")
    print("\n" + "="*70)
    
    # Test URL - use a specific file so counter is visible
    base_url = "http://localhost:8080"
    url = f"{base_url}/Directory/images/README.html"
    num_requests = 50
    
    # Check if server is running
    print(f"\nChecking if server is running at {base_url}...")
    if not check_server(base_url):
        print("\n❌ ERROR: Server is not responding!")
        print("\nPlease start the server first:")
        print("\n  For testing WITH race condition:")
        print("    python server.py collection --no-lock --no-rate-limit")
        print("\n  For testing WITHOUT race condition:")
        print("    python server.py collection --no-rate-limit")
        print("\nThen run this test again.")
        return
    
    print("✅ Server is running!\n")
    
    print("\n" + "="*70)
    print(f"Starting test with {num_requests} concurrent requests...")
    print(f"Target: {url}")
    print("="*70)
    
    successful = test_counter_race(url, num_requests=num_requests, max_workers=25)
    
    # Give server a moment to finish processing
    time.sleep(0.5)
    
    # Check the actual counter value from the directory listing
    print("\n" + "="*70)
    print("CHECKING COUNTER VALUE FROM DIRECTORY LISTING")
    print("="*70)
    
    counter_value = get_counter_value(base_url, "Directory/images/README.html")
    
    if counter_value is not None:
        print(f"\n✅ Successfully retrieved counter from directory listing!")
        print(f"\n📊 RESULTS:")
        print(f"   • Requests sent:    {num_requests}")
        print(f"   • Requests success: {successful}")
        print(f"   • Counter shows:    {counter_value} hits")
        
        if counter_value == successful:
            print(f"\n✅ PASS: Counter is accurate ({counter_value} == {successful})")
            print(f"   Server is using LOCKS (thread-safe)")
        else:
            lost_count = successful - counter_value
            loss_percent = (lost_count / successful * 100) if successful > 0 else 0
            print(f"\n❌ RACE CONDITION DETECTED!")
            print(f"   Counter shows:  {counter_value}")
            print(f"   Should be:      {successful}")
            print(f"   Lost counts:    {lost_count} ({loss_percent:.1f}% loss)")
            print(f"\n   Server is NOT using locks (race condition present)")
    else:
        print(f"\n⚠️  Could not retrieve counter value automatically.")
        print(f"   Please check manually in browser:")
    
    print("\n" + "="*70)
    print("MANUAL VERIFICATION:")
    print("="*70)
    print(f"\n1. Open your browser to: http://localhost:8080/Directory/images/")
    print(f"2. Look at the hit counter for 'README.html'")
    print(f"\nEXPECTED RESULTS:")
    print(f"  • Successful requests: {successful}")
    print(f"\n  • WITH LOCKS (--no-lock NOT used):")
    print(f"    Hit counter should show: {successful} hits ✓")
    print(f"\n  • WITHOUT LOCKS (--no-lock used):")
    print(f"    Hit counter will show: LESS than {successful} hits ✗")
    print(f"    (This demonstrates the race condition!)")
    print(f"\nWhy? Multiple threads read the same counter value simultaneously,")
    print(f"then overwrite each other's updates, causing lost increments.")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
