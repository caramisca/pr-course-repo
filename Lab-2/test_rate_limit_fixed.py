"""
Fixed Rate Limiting Test - Uses threading to send requests properly
"""

import requests
import time
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor


def check_server(url):
    """Check if server is running"""
    try:
        requests.get(url, timeout=2)
        return True
    except:
        return False


class RateLimitTest:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.results = {
            'successful': 0,
            'blocked': 0,
            'errors': 0,
            'response_times': []
        }
        self.lock = threading.Lock()
    
    def make_request(self):
        """Make a single request and record result"""
        start = time.time()
        try:
            response = requests.get(f"{self.base_url}/Directory/images/README.html", timeout=3)
            elapsed = time.time() - start
            
            with self.lock:
                self.results['response_times'].append(elapsed)
                if response.status_code == 200:
                    self.results['successful'] += 1
                elif response.status_code == 429:
                    self.results['blocked'] += 1
                else:
                    self.results['errors'] += 1
                    
        except Exception as e:
            with self.lock:
                self.results['errors'] += 1
    
    def spam_test(self, duration=10, requests_per_second=20):
        """
        Send requests at specified rate using ThreadPoolExecutor
        
        Args:
            duration: Test duration in seconds
            requests_per_second: Target request rate
        """
        print(f"\n{'='*70}")
        print(f"RATE LIMIT TEST: {requests_per_second} req/s for {duration} seconds")
        print(f"Expected: ~{duration * requests_per_second} total requests")
        print(f"Server limit: 5 req/s (should block ~{duration * (requests_per_second - 5)} requests)")
        print(f"{'='*70}\n")
        
        interval = 1.0 / requests_per_second
        end_time = time.time() + duration
        request_count = 0
        
        # Use ThreadPoolExecutor to send requests without blocking
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            
            while time.time() < end_time:
                # Submit request to thread pool
                future = executor.submit(self.make_request)
                futures.append(future)
                request_count += 1
                
                # Progress indicator
                if request_count % 50 == 0:
                    print(f"  Sent {request_count} requests...")
                
                # Sleep to maintain rate
                time.sleep(interval)
            
            print(f"\n  Waiting for all {request_count} requests to complete...")
            # Wait for all requests to finish
            for future in futures:
                future.result()
        
        # Print results
        total = self.results['successful'] + self.results['blocked'] + self.results['errors']
        
        print(f"\n{'='*70}")
        print(f"TEST RESULTS")
        print(f"{'='*70}")
        print(f"  Total requests sent:     {request_count}")
        print(f"  Total completed:         {total}")
        print(f"  Successful (200):        {self.results['successful']} ({self.results['successful']/total*100:.1f}%)")
        print(f"  Blocked (429):           {self.results['blocked']} ({self.results['blocked']/total*100:.1f}%)")
        print(f"  Errors:                  {self.results['errors']}")
        
        if self.results['response_times']:
            avg_time = sum(self.results['response_times']) / len(self.results['response_times'])
            print(f"\n  Average response time:   {avg_time:.3f}s")
            print(f"  Min response time:       {min(self.results['response_times']):.3f}s")
            print(f"  Max response time:       {max(self.results['response_times']):.3f}s")
        
        actual_throughput = self.results['successful'] / duration
        print(f"\n  Successful throughput:   {actual_throughput:.2f} req/s")
        print(f"  Expected limit:          5.00 req/s")
        
        print(f"{'='*70}\n")
        
        # Verify rate limiting works
        if 4.0 <= actual_throughput <= 6.0:
            print("✅ PASS: Rate limiting is working! Throughput is ~5 req/s")
        else:
            print(f"❌ FAIL: Rate limiting may not be working (throughput: {actual_throughput:.2f} req/s)")


def main():
    base_url = "http://localhost:8080"
    
    # Check server
    print(f"\nChecking if server is running at {base_url}...")
    if not check_server(base_url):
        print("\n❌ ERROR: Server is not responding!")
        print("\nPlease start the server first:")
        print("  cd Lab-2")
        print("  python server.py collection")
        return
    
    print("✅ Server is running!\n")
    
    # Run tests
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'light':
        # Light test: 10 req/s for 5 seconds
        test = RateLimitTest(base_url)
        test.spam_test(duration=5, requests_per_second=4)
    else:
        # Full test: 20 req/s for 10 seconds  
        test = RateLimitTest(base_url)
        test.spam_test(duration=10, requests_per_second=20)


if __name__ == "__main__":
    main()
