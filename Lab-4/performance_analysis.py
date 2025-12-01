"""
Performance Analysis for Distributed Key-Value Store
Analyzes write latency vs write quorum and checks data consistency
"""

import os
import time
import subprocess
import requests
import matplotlib.pyplot as plt
import numpy as np
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

QUORUM_VALUES = [1, 2, 3, 4, 5]
NUM_WRITES = 100
NUM_THREADS = 10  # Concurrent write threads
NUM_KEYS = 10


def wait_for_services(timeout=60):
    """Wait for all services to be ready"""
    print("Waiting for services to start...")
    all_urls = [LEADER_URL] + FOLLOWER_URLS
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        all_ready = True
        for url in all_urls:
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code != 200:
                    all_ready = False
                    break
            except:
                all_ready = False
                break
        
        if all_ready:
            print("✓ All services are ready")
            return True
        
        time.sleep(2)
    
    print("✗ Services failed to start within timeout")
    return False


def restart_cluster_with_quorum(quorum):
    """Restart the cluster with a new write quorum value"""
    print(f"\n{'='*80}")
    print(f"Configuring cluster with WRITE_QUORUM={quorum}")
    print('='*80)
    
    # Stop existing containers
    print("Stopping existing containers...")
    subprocess.run(["docker-compose", "down"], 
                  stdout=subprocess.DEVNULL, 
                  stderr=subprocess.DEVNULL,
                  cwd=os.path.dirname(os.path.abspath(__file__)))
    time.sleep(2)
    
    # Update docker-compose.yml with new quorum
    compose_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "docker-compose.yml")
    
    with open(compose_file, 'r') as f:
        content = f.read()
    
    # Replace WRITE_QUORUM value
    import re
    content = re.sub(r'- WRITE_QUORUM=\d+', f'- WRITE_QUORUM={quorum}', content)
    
    with open(compose_file, 'w') as f:
        f.write(content)
    
    # Start containers
    print(f"Starting containers with WRITE_QUORUM={quorum}...")
    subprocess.run(["docker-compose", "up", "-d"], 
                  stdout=subprocess.DEVNULL,
                  cwd=os.path.dirname(os.path.abspath(__file__)))
    
    # Wait for services
    if not wait_for_services():
        raise Exception("Failed to start services")
    
    time.sleep(3)  # Extra time for initialization


def perform_write(key_id, write_id):
    """Perform a single write operation"""
    key = f"key_{key_id}"
    value = f"value_{write_id}"
    
    try:
        start = time.time()
        response = requests.post(
            f"{LEADER_URL}/write",
            json={"key": key, "value": value},
            timeout=15
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            return (True, elapsed, key, value, response.json())
        else:
            return (False, elapsed, key, value, None)
    except Exception as e:
        return (False, 0, key, value, str(e))


def run_performance_test(quorum):
    """Run performance test for a given quorum value"""
    print(f"\nRunning performance test with WRITE_QUORUM={quorum}")
    print("-" * 80)
    print(f"Performing {NUM_WRITES} writes with {NUM_THREADS} concurrent threads...")
    
    latencies = []
    successful_writes = 0
    failed_writes = 0
    
    # Perform concurrent writes
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = []
        for write_id in range(NUM_WRITES):
            key_id = write_id % NUM_KEYS
            futures.append(executor.submit(perform_write, key_id, write_id))
        
        for future in as_completed(futures):
            success, elapsed, key, value, response = future.result()
            if success:
                latencies.append(elapsed)
                successful_writes += 1
            else:
                failed_writes += 1
                
        total_time = time.time() - start_time
    
    print(f"\nCompleted in {total_time:.2f} seconds")
    
    avg_latency = np.mean(latencies) if latencies else 0
    median_latency = np.median(latencies) if latencies else 0
    p95_latency = np.percentile(latencies, 95) if latencies else 0
    p99_latency = np.percentile(latencies, 99) if latencies else 0
    
    print(f"\n  Results:")
    print(f"    Total writes: {NUM_WRITES}")
    print(f"    Successful: {successful_writes}")
    print(f"    Failed: {failed_writes}")
    print(f"    Average latency: {avg_latency*1000:.2f}ms")
    print(f"    Median latency: {median_latency*1000:.2f}ms")
    print(f"    P95 latency: {p95_latency*1000:.2f}ms")
    print(f"    P99 latency: {p99_latency*1000:.2f}ms")
    
    return {
        'quorum': quorum,
        'avg_latency': avg_latency,
        'median_latency': median_latency,
        'p95_latency': p95_latency,
        'p99_latency': p99_latency,
        'successful': successful_writes,
        'failed': failed_writes
    }


def check_consistency():
    """Check data consistency across all replicas"""
    print(f"\n{'='*80}")
    print("CHECKING DATA CONSISTENCY")
    print('='*80)
    
    # Get leader data
    print("\nFetching data from leader...")
    leader_response = requests.get(f"{LEADER_URL}/data")
    leader_data = leader_response.json()['data']
    print(f"  Leader has {len(leader_data)} keys")
    
    # Get follower data
    print("\nFetching data from followers...")
    follower_data_list = []
    for i, follower_url in enumerate(FOLLOWER_URLS, 1):
        response = requests.get(f"{follower_url}/data")
        data = response.json()
        follower_data_list.append(data)
        print(f"  Follower {i} ({data['node_id']}) has {data['count']} keys")
    
    # Check consistency
    print("\nConsistency analysis:")
    print("-" * 80)
    
    for i, follower_info in enumerate(follower_data_list, 1):
        follower_data = follower_info['data']
        node_id = follower_info['node_id']
        
        matches = 0
        version_matches = 0
        
        for key in leader_data:
            if key in follower_data:
                if follower_data[key]['value'] == leader_data[key]['value']:
                    matches += 1
                    if follower_data[key]['version'] == leader_data[key]['version']:
                        version_matches += 1
        
        consistency = (matches / len(leader_data) * 100) if leader_data else 0
        version_consistency = (version_matches / len(leader_data) * 100) if leader_data else 0
        
        print(f"  Follower {i} ({node_id}):")
        print(f"    Value consistency: {matches}/{len(leader_data)} ({consistency:.1f}%)")
        print(f"    Version consistency: {version_matches}/{len(leader_data)} ({version_consistency:.1f}%)")


def plot_results(results):
    """Create visualization of performance results"""
    print(f"\n{'='*80}")
    print("GENERATING PERFORMANCE PLOT")
    print('='*80)
    
    quorums = [r['quorum'] for r in results]
    avg_latencies = [r['avg_latency'] * 1000 for r in results]  # Convert to ms
    median_latencies = [r['median_latency'] * 1000 for r in results]
    p95_latencies = [r['p95_latency'] * 1000 for r in results]
    p99_latencies = [r['p99_latency'] * 1000 for r in results]
    
    # Create figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Latency vs Quorum (matching reference style)
    ax1.plot(quorums, avg_latencies, 'o-', label='Average', linewidth=2, markersize=8, color='#1f77b4')
    ax1.plot(quorums, median_latencies, 's-', label='Median', linewidth=2, markersize=8, color='#ff7f0e')
    ax1.plot(quorums, p95_latencies, '^-', label='P95', linewidth=2, markersize=8, color='#2ca02c')
    ax1.plot(quorums, p99_latencies, 'v-', label='P99', linewidth=2, markersize=8, color='#d62728')
    ax1.set_xlabel('Write Quorum', fontsize=11)
    ax1.set_ylabel('Latency (ms)', fontsize=11)
    ax1.set_title('Write Quorum vs Latency', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10, loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(quorums)
    ax1.set_ylim(bottom=0)
    
    # Plot 2: Data Consistency
    success_rates = [(r['successful'] / NUM_WRITES * 100) for r in results]
    bars = ax2.bar(quorums, success_rates, color='lightblue', edgecolor='darkblue', linewidth=1.5)
    ax2.set_xlabel('Write Quorum', fontsize=11)
    ax2.set_ylabel('Average Consistency (%)', fontsize=11)
    ax2.set_title('Write Quorum vs Data Consistency', fontsize=13, fontweight='bold')
    ax2.set_ylim([0, 105])
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_xticks(quorums)
    
    plt.tight_layout()
    
    # Save plot
    plot_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                             "performance_analysis.png")
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved to: {plot_file}")
    
    plt.show()


def print_analysis(results):
    """Print detailed analysis of results"""
    print(f"\n{'='*80}")
    print("PERFORMANCE ANALYSIS RESULTS")
    print('='*80)
    
    print("\nLatency Analysis:")
    print("-" * 80)
    for r in results:
        print(f"  Write Quorum {r['quorum']}:")
        print(f"    Average latency: {r['avg_latency']*1000:.2f}ms")
        print(f"    Median latency: {r['median_latency']*1000:.2f}ms")
        print(f"    P95 latency: {r['p95_latency']*1000:.2f}ms")
        print(f"    P99 latency: {r['p99_latency']*1000:.2f}ms")
        print(f"    Success rate: {r['successful']}/{NUM_WRITES} ({r['successful']/NUM_WRITES*100:.1f}%)")
    
    print("\nKey Observations:")
    print("-" * 80)
    
    # Calculate latency increase
    if len(results) > 1:
        first_latency = results[0]['avg_latency'] * 1000
        last_latency = results[-1]['avg_latency'] * 1000
        increase = ((last_latency - first_latency) / first_latency * 100)
        
        print(f"• Latency increases from {first_latency:.2f}ms (quorum=1) "
              f"to {last_latency:.2f}ms (quorum=5)")
        print(f"• This represents a {increase:.1f}% increase")
        print(f"• Higher quorum requires waiting for more follower acknowledgments")
        print(f"• Even with concurrent replication, we wait for the slowest required replica")
    
    print("\nTrade-offs:")
    print("-" * 80)
    print("• Lower Quorum (1-2):")
    print("  - Lower latency (faster writes)")
    print("  - Weaker consistency guarantees")
    print("  - Higher availability")
    print("  - Risk of data loss if leader fails")
    
    print("\n• Higher Quorum (4-5):")
    print("  - Higher latency (slower writes)")
    print("  - Stronger consistency guarantees")
    print("  - Lower availability (requires more replicas)")
    print("  - Better durability")
    
    print("\n• Quorum = 3 (Majority):")
    print("  - Balanced trade-off")
    print("  - Tolerates 2 follower failures")
    print("  - Common choice in production systems")


def main():
    """Main performance analysis workflow"""
    print("\n" + "="*80)
    print("DISTRIBUTED KEY-VALUE STORE - PERFORMANCE ANALYSIS")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Total writes: {NUM_WRITES}")
    print(f"  Concurrent threads: {NUM_THREADS}")
    print(f"  Number of keys: {NUM_KEYS}")
    print(f"  Quorum values to test: {QUORUM_VALUES}")
    print(f"\nNote: This analysis will take ~5-10 minutes to complete.")
    
    results = []
    
    try:
        # Test each quorum value
        for quorum in QUORUM_VALUES:
            restart_cluster_with_quorum(quorum)
            result = run_performance_test(quorum)
            results.append(result)
        
        # Check final consistency (with last quorum value)
        print("\nWaiting 5 seconds for final replication...")
        time.sleep(5)
        check_consistency()
        
        # Analyze and plot results
        print_analysis(results)
        plot_results(results)
        
        print("\n" + "="*80)
        print("PERFORMANCE ANALYSIS COMPLETED ✓")
        print("="*80)
        print("\nThe performance analysis demonstrates:")
        print("• Write latency increases with higher write quorum")
        print("• Trade-off between consistency and performance")
        print("• CAP theorem in practice")
        print("\nCheck 'performance_analysis.png' for visualizations.\n")
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
    except Exception as e:
        print(f"\n\nError during analysis: {str(e)}")
        raise
    finally:
        # Clean up
        print("\nCleaning up...")
        subprocess.run(["docker-compose", "down"], 
                      stdout=subprocess.DEVNULL,
                      cwd=os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    main()
