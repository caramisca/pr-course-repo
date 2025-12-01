"""
Integration Tests for Distributed Key-Value Store
Tests basic operations, concurrent writes, replication consistency, and concurrent reads/writes
"""

import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
LEADER_URL = "http://localhost:8000"
FOLLOWER_URLS = [
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003",
    "http://localhost:8004",
    "http://localhost:8005"
]

def wait_for_services():
    """Wait for all services to be ready"""
    print("\n" + "="*80)
    print("WAITING FOR SERVICES TO START")
    print("="*80)
    
    all_urls = [LEADER_URL] + FOLLOWER_URLS
    max_retries = 30
    retry_delay = 2
    
    for url in all_urls:
        for i in range(max_retries):
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✓ {url} is ready")
                    break
            except:
                if i < max_retries - 1:
                    print(f"  Waiting for {url}... ({i+1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print(f"✗ {url} failed to start")
                    raise Exception(f"Service at {url} did not start")
    
    print("\n✓ All services are ready!\n")


def test_basic_write_read():
    """Test 1: Basic write and read operations"""
    print("="*80)
    print("TEST 1: Basic Write and Read Operations")
    print("="*80)
    
    # Write to leader
    print("\n1. Writing key 'test1' to leader...")
    response = requests.post(
        f"{LEADER_URL}/write",
        json={"key": "test1", "value": "hello_world"}
    )
    print(f"   Response: {response.json()}")
    assert response.status_code == 200, f"Write failed: {response.status_code}"
    
    # Read from leader
    print("\n2. Reading key 'test1' from leader...")
    response = requests.get(f"{LEADER_URL}/read?key=test1")
    data = response.json()
    print(f"   Response: {data}")
    assert response.status_code == 200, "Read from leader failed"
    assert data['value'] == "hello_world", "Value mismatch on leader"
    
    # Give time for replication
    print("\n3. Waiting for replication (2 seconds)...")
    time.sleep(2)
    
    # Read from followers
    print("\n4. Reading key 'test1' from all followers...")
    for i, follower_url in enumerate(FOLLOWER_URLS, 1):
        response = requests.get(f"{follower_url}/read?key=test1")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Follower {i} ({data['node_id']}): {data['value']}")
            assert data['value'] == "hello_world", f"Value mismatch on follower {i}"
        else:
            print(f"   ✗ Follower {i} failed: {response.status_code}")
    
    print("\n✓ TEST 1 PASSED\n")


def test_concurrent_writes():
    """Test 2: Concurrent write operations"""
    print("="*80)
    print("TEST 2: Concurrent Write Operations")
    print("="*80)
    
    num_writes = 20
    results = []
    
    def write_key(i):
        key = f"concurrent_key_{i % 5}"  # Write to 5 different keys
        value = f"value_{i}"
        try:
            start = time.time()
            response = requests.post(
                f"{LEADER_URL}/write",
                json={"key": key, "value": value},
                timeout=10
            )
            elapsed = time.time() - start
            return (i, response.status_code, elapsed, response.json())
        except Exception as e:
            return (i, 0, 0, str(e))
    
    print(f"\n1. Performing {num_writes} concurrent writes...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(write_key, i) for i in range(num_writes)]
        for future in as_completed(futures):
            results.append(future.result())
    
    # Analyze results
    successful = sum(1 for _, status, _, _ in results if status == 200)
    avg_latency = sum(elapsed for _, status, elapsed, _ in results if status == 200) / max(successful, 1)
    
    print(f"\n2. Results:")
    print(f"   Total writes: {num_writes}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {num_writes - successful}")
    print(f"   Average latency: {avg_latency*1000:.2f}ms")
    
    assert successful >= num_writes * 0.8, f"Too many failures: {num_writes - successful}"
    
    print("\n✓ TEST 2 PASSED\n")


def test_replication_consistency():
    """Test 3: Check replication consistency"""
    print("="*80)
    print("TEST 3: Replication Consistency")
    print("="*80)
    
    # Write multiple keys
    test_data = {
        f"consistency_key_{i}": f"value_{i}"
        for i in range(10)
    }
    
    print(f"\n1. Writing {len(test_data)} keys to leader...")
    for key, value in test_data.items():
        response = requests.post(
            f"{LEADER_URL}/write",
            json={"key": key, "value": value}
        )
        assert response.status_code == 200, f"Write failed for {key}"
    
    print("\n2. Waiting for replication (3 seconds)...")
    time.sleep(3)
    
    # Check leader data
    print("\n3. Checking leader data...")
    leader_response = requests.get(f"{LEADER_URL}/data")
    leader_data = leader_response.json()['data']
    print(f"   Leader has {len(leader_data)} keys")
    
    # Check each follower
    print("\n4. Checking follower data consistency...")
    for i, follower_url in enumerate(FOLLOWER_URLS, 1):
        response = requests.get(f"{follower_url}/data")
        follower_data = response.json()['data']
        node_id = response.json()['node_id']
        
        # Count matching keys
        matches = 0
        for key in test_data:
            if key in follower_data and key in leader_data:
                if (follower_data[key]['value'] == leader_data[key]['value'] and
                    follower_data[key]['version'] == leader_data[key]['version']):
                    matches += 1
        
        consistency = (matches / len(test_data)) * 100
        print(f"   Follower {i} ({node_id}): {matches}/{len(test_data)} keys match ({consistency:.1f}%)")
        
        assert consistency >= 80, f"Follower {i} consistency too low: {consistency}%"
    
    print("\n✓ TEST 3 PASSED\n")


def test_concurrent_reads_writes():
    """Test 4: Concurrent reads and writes"""
    print("="*80)
    print("TEST 4: Concurrent Reads and Writes")
    print("="*80)
    
    test_key = "concurrent_test"
    num_operations = 50
    results = {"reads": [], "writes": []}
    
    def perform_write(i):
        try:
            start = time.time()
            response = requests.post(
                f"{LEADER_URL}/write",
                json={"key": test_key, "value": f"value_{i}"},
                timeout=10
            )
            elapsed = time.time() - start
            return ("write", response.status_code, elapsed)
        except Exception as e:
            return ("write", 0, 0)
    
    def perform_read(i):
        try:
            # Read from random follower or leader
            urls = [LEADER_URL] + FOLLOWER_URLS
            url = urls[i % len(urls)]
            start = time.time()
            response = requests.get(f"{url}/read?key={test_key}", timeout=5)
            elapsed = time.time() - start
            return ("read", response.status_code, elapsed)
        except Exception as e:
            return ("read", 0, 0)
    
    print(f"\n1. Performing {num_operations} concurrent reads and writes...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for i in range(num_operations):
            if i % 2 == 0:
                futures.append(executor.submit(perform_write, i))
            else:
                futures.append(executor.submit(perform_read, i))
        
        for future in as_completed(futures):
            op_type, status, elapsed = future.result()
            results[f"{op_type}s"].append((status, elapsed))
    
    # Analyze results
    print("\n2. Results:")
    
    write_success = sum(1 for status, _ in results["writes"] if status == 200)
    write_total = len(results["writes"])
    write_avg = sum(elapsed for status, elapsed in results["writes"] if status == 200) / max(write_success, 1)
    
    read_success = sum(1 for status, _ in results["reads"] if status in [200, 404])
    read_total = len(results["reads"])
    read_avg = sum(elapsed for status, elapsed in results["reads"] if status in [200, 404]) / max(read_success, 1)
    
    print(f"   Writes: {write_success}/{write_total} successful (avg: {write_avg*1000:.2f}ms)")
    print(f"   Reads: {read_success}/{read_total} successful (avg: {read_avg*1000:.2f}ms)")
    
    assert write_success >= write_total * 0.8, "Too many write failures"
    assert read_success >= read_total * 0.8, "Too many read failures"
    
    print("\n✓ TEST 4 PASSED\n")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("DISTRIBUTED KEY-VALUE STORE - INTEGRATION TESTS")
    print("="*80)
    
    try:
        # Wait for services
        wait_for_services()
        
        # Run tests
        test_basic_write_read()
        test_concurrent_writes()
        test_replication_consistency()
        test_concurrent_reads_writes()
        
        # Summary
        print("="*80)
        print("ALL TESTS PASSED ✓")
        print("="*80)
        print("\nThe distributed key-value store is working correctly!")
        print("- Basic write/read operations work")
        print("- Concurrent writes are handled properly")
        print("- Replication consistency is maintained")
        print("- Concurrent reads and writes work together")
        print("\n")
        
    except Exception as e:
        print("\n" + "="*80)
        print(f"TEST FAILED ✗")
        print("="*80)
        print(f"Error: {str(e)}\n")
        raise


if __name__ == "__main__":
    main()
