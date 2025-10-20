"""
Counter Race Condition Test - Lab 2
Demonstrates the race condition in request counter with and without locks.
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys


def make_request(url, request_id):
    """Make a single HTTP request"""
    try:
        response = requests.get(url, timeout=10)
        return (request_id, response.status_code)
    except Exception as e:
        return (request_id, f"ERROR: {e}")


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
            request_id, status = future.result()
            
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
    
    # Wait for user
    print("\nMake sure your server is running, then press Enter...")
    input()
    
    # Test URL - use a specific file so counter is visible
    url = "http://localhost:8080/Directory/images/README.html"
    num_requests = 50
    
    print("\n" + "="*70)
    print(f"Starting test with {num_requests} concurrent requests...")
    print(f"Target: {url}")
    print("="*70)
    
    successful = test_counter_race(url, num_requests=num_requests, max_workers=25)
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
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
