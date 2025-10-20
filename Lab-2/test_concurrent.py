"""
Concurrent Request Testing Script - Lab 2
Tests the multithreaded server by making concurrent requests and measuring response times.
Compares performance with single-threaded vs multithreaded server.
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics


def make_request(url, request_id):
    """
    Make a single HTTP request and measure response time
    
    Args:
        url: URL to request
        request_id: Identifier for this request
        
    Returns:
        Tuple of (request_id, response_time, status_code)
    """
    start_time = time.time()
    try:
        response = requests.get(url, timeout=30)
        end_time = time.time()
        response_time = end_time - start_time
        return (request_id, response_time, response.status_code)
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        return (request_id, response_time, f"ERROR: {e}")


def test_concurrent_requests(url, num_requests=10, max_workers=10):
    """
    Test server with concurrent requests
    
    Args:
        url: Base URL to test
        num_requests: Number of concurrent requests to make
        max_workers: Maximum number of worker threads
        
    Returns:
        Dictionary with test results
    """
    print(f"\n{'='*70}")
    print(f"Testing with {num_requests} concurrent requests")
    print(f"URL: {url}")
    print(f"Max workers: {max_workers}")
    print(f"{'='*70}\n")
    
    overall_start = time.time()
    response_times = []
    successful_requests = 0
    failed_requests = 0
    
    # Make concurrent requests
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all requests
        futures = {
            executor.submit(make_request, url, i): i 
            for i in range(num_requests)
        }
        
        # Collect results as they complete
        for future in as_completed(futures):
            request_id, response_time, status = future.result()
            response_times.append(response_time)
            
            if isinstance(status, int) and status == 200:
                successful_requests += 1
                print(f"✓ Request {request_id:2d}: {response_time:.3f}s - Status {status}")
            else:
                failed_requests += 1
                print(f"✗ Request {request_id:2d}: {response_time:.3f}s - {status}")
    
    overall_end = time.time()
    total_time = overall_end - overall_start
    
    # Calculate statistics
    results = {
        'total_time': total_time,
        'num_requests': num_requests,
        'successful': successful_requests,
        'failed': failed_requests,
        'response_times': response_times,
        'min_time': min(response_times) if response_times else 0,
        'max_time': max(response_times) if response_times else 0,
        'avg_time': statistics.mean(response_times) if response_times else 0,
        'median_time': statistics.median(response_times) if response_times else 0,
        'throughput': successful_requests / total_time if total_time > 0 else 0
    }
    
    return results


def print_results(results, label="Test Results"):
    """Print formatted test results"""
    print(f"\n{'='*70}")
    print(f"{label}")
    print(f"{'='*70}")
    print(f"Total time:           {results['total_time']:.3f}s")
    print(f"Total requests:       {results['num_requests']}")
    print(f"Successful requests:  {results['successful']}")
    print(f"Failed requests:      {results['failed']}")
    print(f"\nResponse Time Statistics:")
    print(f"  Min:                {results['min_time']:.3f}s")
    print(f"  Max:                {results['max_time']:.3f}s")
    print(f"  Average:            {results['avg_time']:.3f}s")
    print(f"  Median:             {results['median_time']:.3f}s")
    print(f"\nThroughput:           {results['throughput']:.2f} requests/second")
    print(f"{'='*70}\n")


def compare_servers():
    """
    Compare performance between single-threaded and multithreaded servers
    
    Note: You need to run the servers on different ports or sequentially
    """
    print("\n" + "="*70)
    print("CONCURRENT REQUEST PERFORMANCE TEST")
    print("="*70)
    print("\nThis test compares single-threaded vs multithreaded server performance.")
    print("The server should be configured with a delay (~1s) to simulate work.\n")
    
    # Test parameters
    url = "http://localhost:8080/Directory/images/README.html"
    num_requests = 10
    
    print("\nINSTRUCTIONS:")
    print("1. Start your server with delay: python server.py collection --delay 1")
    print("2. Press Enter when ready...")
    input()
    
    # Test multithreaded server
    print(f"\nTarget: {url}\n")
    mt_results = test_concurrent_requests(url, num_requests=num_requests, max_workers=10)
    print_results(mt_results, "MULTITHREADED SERVER RESULTS")
    
    print("\nCOMPARISON:")
    print(f"If this were a single-threaded server with 1s delay per request,")
    print(f"it would take approximately {num_requests}s to handle all requests.")
    print(f"The multithreaded server took only {mt_results['total_time']:.3f}s")
    print(f"Speedup: {num_requests / mt_results['total_time']:.2f}x faster!\n")
    
    return mt_results


def test_race_condition():
    """
    Test to demonstrate race condition in request counter
    
    Make many concurrent requests to the same file to show counter inconsistency
    """
    print("\n" + "="*70)
    print("RACE CONDITION TEST")
    print("="*70)
    print("\nThis test makes concurrent requests to demonstrate race conditions.")
    print("Start server with: python server.py collection --no-lock")
    print("Then check the hit counter - it should be less than expected.\n")
    
    url = "http://localhost:8080/Directory/images/README.html"
    num_requests = 50
    
    print("Press Enter to start the test...")
    input()
    
    print(f"\nMaking {num_requests} requests to {url}...")
    print(f"Expected hits after test: {num_requests} hits.")
    
    overall_start = time.time()
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_request, url, i) for i in range(num_requests)]
        results = [f.result() for f in as_completed(futures)]
    
    overall_end = time.time()
    
    successful = sum(1 for _, _, status in results if status == 200)
    
    print(f"\nCompleted in {overall_end - overall_start:.3f}s")
    print(f"Successful requests: {successful}")
    print(f"\nNow check the directory listing to see the hit count.")
    print(f"Without locks, the count will likely be LESS than {successful} due to race conditions!")
    print(f"\nRestart with locks enabled (remove --no-lock) and try again.")


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == 'compare':
            compare_servers()
        elif mode == 'race':
            test_race_condition()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python test_concurrent.py [compare|race]")
    else:
        # Default: run comparison test
        print("Usage: python test_concurrent.py [compare|race]")
        print("\nModes:")
        print("  compare  - Compare single-threaded vs multithreaded performance")
        print("  race     - Demonstrate race condition in request counter")
        print("\nRunning comparison test...\n")
        compare_servers()


if __name__ == '__main__':
    main()
