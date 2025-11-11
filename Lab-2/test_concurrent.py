"""
Concurrent Request Testing Script - Lab 2
Tests the multithreaded server by making concurrent requests and measuring response times.

New: "load" mode to test a single, already-running server without any cross-server
comparison. This matches the lab requirement to run servers one after another and
test the currently running server separately. Output is tailored to clearly show
per-request timings, rate-limited counts, and throughput similar to the examples.
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


def test_concurrent_requests(url, num_requests=10, max_workers=10, print_header=True):
    """
    Test server with concurrent requests
    
    Args:
        url: Base URL to test
        num_requests: Number of concurrent requests to make
        max_workers: Maximum number of worker threads
        
    Returns:
        Dictionary with test results
    """
    if print_header:
        print(f"\n{'='*70}")
        print(f"Testing with {num_requests} concurrent requests")
        print(f"URL: {url}")
        print(f"Max workers: {max_workers}")
        print(f"{'='*70}\n")
    
    overall_start = time.time()
    response_times = []
    successful_requests = 0
    failed_requests = 0
    rate_limited = 0
    
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

            if isinstance(status, int):
                if status == 200:
                    successful_requests += 1
                    print(f"Request {request_id+1}: SUCCESS, Time: {response_time:.3f}s")
                elif status == 429:
                    rate_limited += 1
                    print(f"Request {request_id+1}: HTTP 429, Time: {response_time:.3f}s")
                else:
                    failed_requests += 1
                    print(f"Request {request_id+1}: HTTP {status}, Time: {response_time:.3f}s")
            else:
                failed_requests += 1
                print(f"Request {request_id+1}: ERROR, Time: {response_time:.3f}s")
    
    overall_end = time.time()
    total_time = overall_end - overall_start
    
    # Calculate statistics
    results = {
        'total_time': total_time,
        'num_requests': num_requests,
        'successful': successful_requests,
        'failed': failed_requests,
        'rate_limited': rate_limited,
        'response_times': response_times,
        'min_time': min(response_times) if response_times else 0,
        'max_time': max(response_times) if response_times else 0,
        'avg_time': statistics.mean(response_times) if response_times else 0,
        'median_time': statistics.median(response_times) if response_times else 0,
        'throughput': successful_requests / total_time if total_time > 0 else 0,
        'total_throughput': num_requests / total_time if total_time > 0 else 0
    }
    
    return results


def print_results(results, label="Test Results"):
    """Print formatted test results in a concise, screenshot-like format"""
    print("\n== Test Results ==")
    print(f"Total time: {results['total_time']:.2f}s")
    print(f"Total requests: {results['num_requests']}")
    print(f"Successful requests: {results['successful']}")
    print(f"Rate limited (429): {results.get('rate_limited', 0)}")
    print(f"Other errors: {results['failed']}")

    print("\n== Response Time Stats ==")
    print(f"Average response time: {results['avg_time']:.3f}s")
    print(f"Min response time: {results['min_time']:.3f}s")
    print(f"Max response time: {results['max_time']:.3f}s")

    success_rate = (results['successful'] / results['num_requests'] * 100.0) if results['num_requests'] else 0.0
    print("\n== Throughput Stats ==")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Successful throughput: {results['throughput']:.2f} requests/second")
    print(f"Total throughput: {results['total_throughput']:.2f} requests/second")


def compare_servers():
    """
    Compare performance between single-threaded and multithreaded servers
    
    Tests Lab 1 single-threaded server vs Lab 2 multithreaded server
    """
    print("\n" + "="*70)
    print("CONCURRENT REQUEST PERFORMANCE TEST")
    print("="*70)
    print("\nThis test compares single-threaded vs multithreaded server performance.")
    print("using actual servers from Lab 1 and Lab 2.\n")
    
    # Test parameters
    num_requests = 10
    
    print("\n" + "="*70)
    print("SETUP INSTRUCTIONS")
    print("="*70)
    print("\nOption 1: Test with Docker containers")
    print("  1. Start Lab 1 single-threaded server:")
    print("     cd ../Lab 1")
    print("     docker-compose up -d")
    print("     (This will run on port 8080)")
    print("\n  2. In another terminal, start Lab 2 multithreaded server:")
    print("     cd ../Lab-2")
    print("     python server.py collection --delay 1")
    print("     (This will run on port 8080 after stopping Lab 1)")
    print("\nOption 2: Test with local servers on different ports")
    print("  1. Start Lab 1 server:")
    print("     cd ../Lab 1")
    print("     python server.py collection")
    print("     (Running on port 8080)")
    print("\n  2. Modify Lab 2 server to use port 8081 and start it:")
    print("     cd ../Lab-2")
    print("     # Edit server.py port or use: python server.py collection --delay 1")
    print("="*70)
    
    # Test single-threaded server (Lab 1)
    print("\n\n" + "="*70)
    print("TEST 1: SINGLE-THREADED SERVER (Lab 1)")
    print("="*70)
    print("\nMake sure Lab 1 server is running on http://localhost:8080")
    print("Press Enter when ready...")
    input()
    
    lab1_url = "http://localhost:8080/"
    print(f"\nTesting: {lab1_url}")
    print(f"Making {num_requests} concurrent requests...\n")
    
    st_results = test_concurrent_requests(lab1_url, num_requests=num_requests, max_workers=10)
    print_results(st_results, "SINGLE-THREADED SERVER (Lab 1) RESULTS")
    
    # Pause between tests
    print("\n" + "="*70)
    print("Now stop Lab 1 server and start Lab 2 server")
    print("="*70)
    print("\nStop Lab 1 server:")
    print("  - Docker: cd ../Lab 1 && docker-compose down")
    print("  - Local: Ctrl+C in Lab 1 terminal")
    print("\nStart Lab 2 server with delay:")
    print("  python server.py collection --delay 1")
    print("\nPress Enter when Lab 2 server is ready...")
    input()
    
    # Test multithreaded server (Lab 2)
    print("\n\n" + "="*70)
    print("TEST 2: MULTITHREADED SERVER (Lab 2)")
    print("="*70)
    
    lab2_url = "http://localhost:8080/Directory/images/README.html"
    print(f"\nTesting: {lab2_url}")
    print(f"Making {num_requests} concurrent requests with 1s delay per request...\n")
    
    mt_results = test_concurrent_requests(lab2_url, num_requests=num_requests, max_workers=10)
    print_results(mt_results, "MULTITHREADED SERVER (Lab 2) RESULTS")
    
    # Final comparison
    # No cross-server overall/speedup calculation — keep results separate per requirement.
    print("\n" + "="*70)
    print("Run completed. Review the per-server results above.")
    print("="*70 + "\n")
    
    return {'single_threaded': st_results, 'multithreaded': mt_results}


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

        if mode == 'load':
            # Usage: python test_concurrent.py load <url> [num_requests] [max_workers]
            if len(sys.argv) < 3:
                print("Usage: python test_concurrent.py load <url> [num_requests] [max_workers]")
                sys.exit(1)

            url = sys.argv[2]
            num_requests = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            max_workers = int(sys.argv[4]) if len(sys.argv) > 4 else min(20, num_requests)

            print("\n== Concurrent Load Test ==")
            print(f"Making {num_requests} concurrent requests to {url}")

            results = test_concurrent_requests(url, num_requests=num_requests, max_workers=max_workers, print_header=False)
            print_results(results, "LOAD TEST RESULTS")

        elif mode == 'compare':
            compare_servers()
        elif mode == 'race':
            test_race_condition()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python test_concurrent.py [load|compare|race]")
    else:
        # Default: guidance
        print("Usage: python test_concurrent.py [load|compare|race]")
        print("\nModes:")
        print("  load     - Run a single-server load test: load <url> [num] [workers]")
        print("  compare  - Compare single-threaded vs multithreaded performance")
        print("  race     - Demonstrate race condition in request counter")
        print("\nNo mode selected — nothing executed.")


if __name__ == '__main__':
    main()
