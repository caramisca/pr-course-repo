"""
Rate Limiting Test Script - Lab 2
Tests the rate limiting feature by making requests at different rates.
Simulates both spam requests and legitimate traffic.
"""

import requests
import time
import threading
from collections import defaultdict


def check_server(url):
    """
    Check if the server is running
    
    Args:
        url: Base URL of the server to check
        
    Returns:
        True if server is responding, False otherwise
    """
    try:
        response = requests.get(url, timeout=2)
        return True
    except:
        return False


class RateLimitTester:
    """Test rate limiting functionality"""
    
    def __init__(self, base_url="http://localhost:8080", test_path="/Directory/images/README.html"):
        self.base_url = base_url
        self.test_path = test_path
        self.results = defaultdict(lambda: {'successful': 0, 'blocked': 0, 'errors': 0})
        self.lock = threading.Lock()
    
    def make_request(self, client_name):
        """
        Make a single request and record the result
        
        Args:
            client_name: Name identifier for the client
        """
        try:
            response = requests.get(f"{self.base_url}{self.test_path}", timeout=5)
            
            with self.lock:
                if response.status_code == 200:
                    self.results[client_name]['successful'] += 1
                elif response.status_code == 429:  # Too Many Requests
                    self.results[client_name]['blocked'] += 1
                else:
                    self.results[client_name]['errors'] += 1
                    print(f"  [UNEXPECTED] {client_name}: HTTP {response.status_code}")
                    
        except requests.exceptions.Timeout:
            with self.lock:
                self.results[client_name]['errors'] += 1
                print(f"  [TIMEOUT] {client_name}: Request timed out after 5s")
        except requests.exceptions.ConnectionError:
            with self.lock:
                self.results[client_name]['errors'] += 1
                print(f"  [ERROR] {client_name}: Connection refused - server not running?")
        except Exception as e:
            with self.lock:
                self.results[client_name]['errors'] += 1
                print(f"  [ERROR] {client_name}: {type(e).__name__}: {e}")
    
    def spam_client(self, duration=10, requests_per_second=20):
        """
        Simulate a spam client that exceeds rate limits
        
        Args:
            duration: How long to spam (seconds)
            requests_per_second: Request rate (default 20 req/s, which is 4x the 5 req/s limit)
        """
        print(f"\n[SPAM CLIENT] Starting spam at {requests_per_second} req/s for {duration}s...")
        print(f"[SPAM CLIENT] Expected total: ~{duration * requests_per_second} requests")
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration:
            self.make_request('spam_client')
            request_count += 1
            
            # Sleep to maintain desired rate
            sleep_time = 1.0 / requests_per_second
            time.sleep(sleep_time)
        
        print(f"[SPAM CLIENT] Completed {request_count} requests in {time.time() - start_time:.2f}s")
    
    def legitimate_client(self, duration=10, requests_per_second=4):
        """
        Simulate a legitimate client that stays below rate limit
        
        Args:
            duration: How long to run (seconds)
            requests_per_second: Request rate (below limit, default 4 req/s < 5 req/s limit)
        """
        print(f"\n[LEGIT CLIENT] Starting legitimate traffic at {requests_per_second} req/s for {duration}s...")
        print(f"[LEGIT CLIENT] Expected total: ~{duration * requests_per_second} requests")
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration:
            self.make_request('legit_client')
            request_count += 1
            
            # Sleep to maintain desired rate
            sleep_time = 1.0 / requests_per_second
            time.sleep(sleep_time)
        
        print(f"[LEGIT CLIENT] Completed {request_count} requests in {time.time() - start_time:.2f}s")
    
    def print_results(self):
        """Print formatted test results"""
        print("\n" + "="*70)
        print("RATE LIMITING TEST RESULTS")
        print("="*70)
        
        for client, stats in self.results.items():
            total = stats['successful'] + stats['blocked'] + stats['errors']
            success_rate = (stats['successful'] / total * 100) if total > 0 else 0
            block_rate = (stats['blocked'] / total * 100) if total > 0 else 0
            
            print(f"\n{client.upper()}:")
            print(f"  Total requests:       {total}")
            print(f"  Successful (200):     {stats['successful']} ({success_rate:.1f}%)")
            print(f"  Blocked (429):        {stats['blocked']} ({block_rate:.1f}%)")
            print(f"  Errors:               {stats['errors']}")
            
            if total > 0:
                throughput = stats['successful'] / 10  # 10 second duration
                print(f"  Throughput:           {throughput:.2f} successful req/s")
        
        print("\n" + "="*70)


def test_single_client_rate_limit():
    """
    Test rate limiting with a single client
    Shows the rate limiter in action
    """
    print("\n" + "="*70)
    print("SINGLE CLIENT RATE LIMIT TEST")
    print("="*70)
    print("\nThis test shows how rate limiting works with a single client.")
    print("Server should be configured with rate limit (e.g., 5 req/s)")
    
    base_url = "http://localhost:8080"
    test_path = "/Directory/images/README.html"
    
    # Check if server is running
    print(f"\nChecking if server is running at {base_url}...")
    if not check_server(base_url):
        print("\n❌ ERROR: Server is not responding!")
        print("\nPlease start the server first:")
        print("  cd Lab-2")
        print("  python server.py collection")
        print("\nThen run this test again.")
        return
    
    print("✅ Server is running!\n")
    
    # Test 1: Send requests at exactly the rate limit
    print("\n--- Test 1: Sending at rate limit (5 req/s) ---")
    print(f"Target: {base_url}{test_path}")
    tester1 = RateLimitTester(base_url, test_path)
    tester1.legitimate_client(duration=5, requests_per_second=5)
    tester1.print_results()
    
    time.sleep(2)  # Wait a bit between tests
    
    # Test 2: Send requests above the rate limit
    print("\n--- Test 2: Sending above rate limit (10 req/s) ---")
    print(f"Target: {base_url}{test_path}")
    tester2 = RateLimitTester(base_url, test_path)
    tester2.spam_client(duration=5, requests_per_second=10)
    tester2.print_results()


def test_concurrent_clients():
    """
    Test rate limiting with concurrent clients
    Simulates one spam client and one legitimate client
    """
    print("\n" + "="*70)
    print("CONCURRENT CLIENTS RATE LIMIT TEST")
    print("="*70)
    print("\nThis test simulates two clients accessing the server concurrently:")
    print("  1. Spam client: ~20 req/s (should be blocked)")
    print("  2. Legitimate client: ~4 req/s (should succeed)")
    print("\nServer should be configured with rate limit (e.g., 5 req/s per IP)")
    print("\nNote: Both clients will appear to come from localhost (same IP).")
    print("In a real scenario, they would have different IPs.")
    print("\nStart server with: python server.py collection")
    print("Press Enter when ready...")
    input()
    
    base_url = "http://localhost:8080"
    test_path = "/Directory/images/README.html"
    duration = 10

    print(f"\nTarget: {base_url}{test_path}")
    tester = RateLimitTester(base_url, test_path)

    # Create threads for spam and legitimate clients
    spam_thread = threading.Thread(
        target=tester.spam_client,
        args=(duration, 20)
    )
    
    legit_thread = threading.Thread(
        target=tester.legitimate_client,
        args=(duration, 4)
    )
    
    # Start both clients
    print(f"\nStarting test for {duration} seconds...")
    start_time = time.time()
    
    spam_thread.start()
    legit_thread.start()
    
    # Wait for completion
    spam_thread.join()
    legit_thread.join()
    
    end_time = time.time()
    
    print(f"\nTest completed in {end_time - start_time:.2f}s")
    
    # Print results
    tester.print_results()
    
    print("\nNOTE: Since both clients run from localhost, they share the same")
    print("rate limit. In a real scenario with different IPs, each would have")
    print("their own independent rate limit.")


def test_burst_traffic():
    """
    Test how rate limiter handles burst traffic
    """
    print("\n" + "="*70)
    print("BURST TRAFFIC TEST")
    print("="*70)
    print("\nThis test sends bursts of requests to see rate limiter behavior.")
    print("\nStart server with: python server.py collection")
    print("Press Enter when ready...")
    input()
    
    base_url = "http://localhost:8080"
    test_path = "/Directory/images/README.html"
    
    print(f"\nTarget: {base_url}{test_path}")
    print("Sending 3 bursts of 10 requests each...")
    
    for burst in range(3):
        print(f"\n--- Burst {burst + 1} ---")
        tester = RateLimitTester(base_url, test_path)
        
        # Send burst
        start_time = time.time()
        threads = []
        for i in range(10):
            thread = threading.Thread(target=tester.make_request, args=(f'burst_{burst + 1}',))
            thread.start()
            threads.append(thread)
        
        # Wait for all requests to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Print results
        stats = tester.results[f'burst_{burst + 1}']
        print(f"Time: {end_time - start_time:.3f}s")
        print(f"Successful: {stats['successful']}, Blocked: {stats['blocked']}, Errors: {stats['errors']}")
        
        # Wait before next burst
        if burst < 2:
            print("Waiting 2 seconds before next burst...")
            time.sleep(2)


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == 'single':
            test_single_client_rate_limit()
        elif mode == 'concurrent':
            test_concurrent_clients()
        elif mode == 'burst':
            test_burst_traffic()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python test_rate_limit.py [single|concurrent|burst]")
    else:
        print("Usage: python test_rate_limit.py [single|concurrent|burst]")
        print("\nModes:")
        print("  single      - Test rate limiting with a single client")
        print("  concurrent  - Test with spam client and legitimate client")
        print("  burst       - Test rate limiter with burst traffic")
        print("\nRunning concurrent test by default...\n")
        test_concurrent_clients()


if __name__ == '__main__':
    main()
