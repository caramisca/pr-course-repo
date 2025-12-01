"""
Example Usage Script
Demonstrates basic operations of the distributed key-value store
"""

import time
import requests
import json

LEADER_URL = "http://localhost:8000"
FOLLOWER_URLS = [
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003",
    "http://localhost:8004",
    "http://localhost:8005"
]


def print_section(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(title)
    print("="*80 + "\n")


def check_health():
    """Check health of all nodes"""
    print_section("1. CHECKING NODE HEALTH")
    
    # Check leader
    print("Leader:")
    response = requests.get(f"{LEADER_URL}/health")
    print(f"  {json.dumps(response.json(), indent=2)}")
    
    # Check followers
    print("\nFollowers:")
    for i, url in enumerate(FOLLOWER_URLS, 1):
        response = requests.get(f"{url}/health")
        data = response.json()
        print(f"  Follower {i} ({data['node_id']}): {data['status']}")


def write_examples():
    """Perform some example writes"""
    print_section("2. WRITING DATA TO LEADER")
    
    examples = [
        {"key": "name", "value": "John Doe"},
        {"key": "age", "value": "30"},
        {"key": "city", "value": "New York"},
        {"key": "occupation", "value": "Software Engineer"},
        {"key": "hobby", "value": "Photography"}
    ]
    
    for example in examples:
        print(f"Writing: {example['key']} = {example['value']}")
        response = requests.post(
            f"{LEADER_URL}/write",
            json=example
        )
        result = response.json()
        print(f"  Status: {result['status']}")
        print(f"  Latency: {result.get('latency_ms', 'N/A')}ms")
        print(f"  Acknowledged by: {result.get('acknowledged_by', 'N/A')}/{result.get('total_followers', 'N/A')} followers")
        print()


def read_from_leader():
    """Read data from leader"""
    print_section("3. READING DATA FROM LEADER")
    
    keys = ["name", "age", "city"]
    
    for key in keys:
        response = requests.get(f"{LEADER_URL}/read?key={key}")
        if response.status_code == 200:
            data = response.json()
            print(f"{key}: {data['value']} (version {data['version']})")
        else:
            print(f"{key}: Not found")


def read_from_followers():
    """Read data from followers"""
    print_section("4. READING DATA FROM FOLLOWERS")
    
    print("Waiting for replication (2 seconds)...")
    time.sleep(2)
    print()
    
    key = "name"
    print(f"Reading key '{key}' from all followers:\n")
    
    for i, url in enumerate(FOLLOWER_URLS, 1):
        response = requests.get(f"{url}/read?key={key}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Follower {i} ({data['node_id']}): {data['value']} (version {data['version']})")
        else:
            print(f"  Follower {i}: Not found")


def get_all_data():
    """Get all data from leader and followers"""
    print_section("5. GETTING ALL DATA")
    
    # Leader data
    print("Leader data:")
    response = requests.get(f"{LEADER_URL}/data")
    data = response.json()
    print(f"  Total keys: {data['count']}")
    print(f"  Keys: {', '.join(data['data'].keys())}")
    
    # Follower data
    print("\nFollower data:")
    for i, url in enumerate(FOLLOWER_URLS, 1):
        response = requests.get(f"{url}/data")
        data = response.json()
        print(f"  Follower {i} ({data['node_id']}): {data['count']} keys")


def test_concurrent_writes():
    """Test concurrent writes"""
    print_section("6. TESTING CONCURRENT WRITES")
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def write_key(i):
        key = f"test_{i}"
        value = f"concurrent_value_{i}"
        start = time.time()
        response = requests.post(
            f"{LEADER_URL}/write",
            json={"key": key, "value": value},
            timeout=10
        )
        elapsed = time.time() - start
        return (i, response.status_code, elapsed)
    
    print("Performing 10 concurrent writes...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(write_key, i) for i in range(10)]
        results = [future.result() for future in as_completed(futures)]
    
    successful = sum(1 for _, status, _ in results if status == 200)
    avg_latency = sum(elapsed for _, status, elapsed in results if status == 200) / max(successful, 1)
    
    print(f"\nResults:")
    print(f"  Successful: {successful}/10")
    print(f"  Average latency: {avg_latency*1000:.2f}ms")


def main():
    """Main example workflow"""
    print("\n" + "="*80)
    print("DISTRIBUTED KEY-VALUE STORE - EXAMPLE USAGE")
    print("="*80)
    
    print("\nMake sure the cluster is running:")
    print("  docker-compose up -d")
    print("\nPress Enter to continue...")
    input()
    
    try:
        check_health()
        write_examples()
        read_from_leader()
        read_from_followers()
        get_all_data()
        test_concurrent_writes()
        
        print_section("EXAMPLE USAGE COMPLETED")
        print("All operations completed successfully!")
        print("\nNext steps:")
        print("  - Run integration tests: python integration_test.py")
        print("  - Run performance analysis: python performance_analysis.py")
        print("  - Explore the API endpoints yourself")
        print()
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the cluster")
        print("Make sure the cluster is running: docker-compose up -d\n")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")


if __name__ == "__main__":
    main()
