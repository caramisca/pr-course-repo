"""
Performance Comparison Test - Lab 1 vs Lab 2
Compares single-threaded (Lab 1) vs multithreaded (Lab 2) server performance.

Usage:
    python test_performance_comparison.py
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import sys


def check_server(url, server_name):
    """Check if a server is running and responsive"""
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"✓ {server_name} is RUNNING and responsive on {url}")
            return True
        else:
            print(f"✗ {server_name} responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ {server_name} is NOT RUNNING on {url}")
        print(f"   Connection refused - server not started")
        return False
    except requests.exceptions.Timeout:
        print(f"✗ {server_name} TIMEOUT on {url}")
        return False
    except Exception as e:
        print(f"✗ {server_name} ERROR: {e}")
        return False


def make_request(url, request_id):
    """Make a single HTTP request and measure response time"""
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


def test_server(url, num_requests=10):
    """Test a server with concurrent requests"""
    print(f"\nMaking {num_requests} concurrent requests to {url}...")
    
    overall_start = time.time()
    response_times = []
    successful_requests = 0
    
    # Make concurrent requests
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = {executor.submit(make_request, url, i): i for i in range(num_requests)}
        
        for future in as_completed(futures):
            request_id, response_time, status = future.result()
            response_times.append(response_time)
            
            if isinstance(status, int) and status == 200:
                successful_requests += 1
                print(f"Request {request_id + 1:2d}: SUCCESS, Time: {response_time:.3f}s")
            else:
                print(f"Request {request_id + 1:2d}: {status}, Time: {response_time:.3f}s")
    
    overall_end = time.time()
    total_time = overall_end - overall_start
    
    return {
        'total_time': total_time,
        'num_requests': num_requests,
        'successful': successful_requests,
        'response_times': response_times,
        'min_time': min(response_times) if response_times else 0,
        'max_time': max(response_times) if response_times else 0,
        'avg_time': statistics.mean(response_times) if response_times else 0,
    }


def print_results(results, server_name):
    """Print formatted test results"""
    print(f"\n{'='*70}")
    print(f"{server_name} RESULTS")
    print(f"{'='*70}")
    print(f"Total time:            {results['total_time']:.3f}s")
    print(f"Total requests:        {results['num_requests']}")
    print(f"Successful requests:   {results['successful']}")
    print(f"Average response time: {results['avg_time']:.3f}s")
    print(f"Min response time:     {results['min_time']:.3f}s")
    print(f"Max response time:     {results['max_time']:.3f}s")
    print(f"{'='*70}")


def main():
    print("="*70)
    print("PERFORMANCE COMPARISON: SINGLE-THREADED vs MULTITHREADED")
    print("="*70)
    print("\nThis test compares Lab 1 (single-threaded) with Lab 2 (multithreaded).")
    print("Both servers MUST be started with --delay 1 flag BEFORE running this test.\n")
    
    print("SETUP INSTRUCTIONS:")
    print("-" * 70)
    print("\n1. Open Terminal 1, start Lab 1 single-threaded server:")
    print("   cd \"D:\\Labs PR\\Lab 1\"")
    print("   python server.py collection --delay 1")
    print("   (Server will run on port 8081)")
    print("\n2. Open Terminal 2, start Lab 2 multithreaded server:")
    print("   cd \"D:\\Labs PR\\Lab-2\"")
    print("   python server.py collection --delay 1")
    print("   (Server will run on port 8080)")
    print("\n3. Press Enter when both servers are ready...")
    input()
    
    # Test parameters
    num_requests = 10
    lab1_url = "http://localhost:8081/"
    lab2_url = "http://localhost:8080/"
    
    # Check if servers are running
    print("\n" + "="*70)
    print("CHECKING SERVER STATUS")
    print("="*70 + "\n")
    
    lab1_running = check_server(lab1_url, "Lab 1 Server (port 8081)")
    lab2_running = check_server(lab2_url, "Lab 2 Server (port 8080)")
    
    if not lab1_running or not lab2_running:
        print("\n" + "="*70)
        print("ERROR: ONE OR BOTH SERVERS NOT RUNNING")
        print("="*70)
        print("\nPlease start the servers before running this test:")
        if not lab1_running:
            print("\n  Lab 1 (Terminal 1):")
            print("  cd \"D:\\Labs PR\\Lab 1\"")
            print("  python server.py collection --delay 1")
        if not lab2_running:
            print("\n  Lab 2 (Terminal 2):")
            print("  cd \"D:\\Labs PR\\Lab-2\"")
            print("  python server.py collection --delay 1")
        print("\nThen run this test again.")
        print("="*70 + "\n")
        sys.exit(1)
    
    print("\n✓ Both servers are running! Starting performance test...\n")
    
    # Test Lab 1 (single-threaded)
    print("\n" + "="*70)
    print("TEST 1: LAB 1 - SINGLE-THREADED SERVER")
    print("="*70)
    print(f"URL: {lab1_url}")
    print(f"With 1-second delay per request, 10 requests should take ~10 seconds")
    
    lab1_results = test_server(lab1_url, num_requests)
    print_results(lab1_results, "LAB 1 - SINGLE-THREADED")
    
    # Wait a moment between tests
    print("\n\nPress Enter to test Lab 2 multithreaded server...")
    input()
    
    # Test Lab 2 (multithreaded)
    print("\n" + "="*70)
    print("TEST 2: LAB 2 - MULTITHREADED SERVER")
    print("="*70)
    print(f"URL: {lab2_url}")
    print(f"With 1-second delay per request, 10 concurrent requests should take ~1 second")
    
    lab2_results = test_server(lab2_url, num_requests)
    print_results(lab2_results, "LAB 2 - MULTITHREADED")
    
    # Comparison
    print("\n\n" + "="*70)
    print("PERFORMANCE COMPARISON")
    print("="*70)
    
    if lab1_results['successful'] == 0 or lab2_results['successful'] == 0:
        print("\n✗ Cannot compare - one or both servers had no successful requests")
        if lab1_results['successful'] == 0:
            print("  Lab 1: All requests failed")
        if lab2_results['successful'] == 0:
            print("  Lab 2: All requests failed")
        print("\nPlease check if servers are still running with correct --delay 1 flag")
    else:
        print(f"\nLab 1 (Single-threaded): {lab1_results['total_time']:.3f}s ({lab1_results['successful']}/{lab1_results['num_requests']} successful)")
        print(f"Lab 2 (Multithreaded):   {lab2_results['total_time']:.3f}s ({lab2_results['successful']}/{lab2_results['num_requests']} successful)")
        
        if lab1_results['total_time'] > 0 and lab2_results['total_time'] > 0:
            speedup = lab1_results['total_time'] / lab2_results['total_time']
            print(f"\n✓ Speedup: {speedup:.2f}x faster")
            print(f"✓ Time saved: {lab1_results['total_time'] - lab2_results['total_time']:.3f}s")
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print("\nMultithreading allows the server to process requests concurrently,")
    print("significantly reducing total time when handling multiple simultaneous requests.")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
