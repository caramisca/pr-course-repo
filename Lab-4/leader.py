"""
Leader Node for Distributed Key-Value Store
Implements single-leader replication with semi-synchronous replication strategy
"""

import os
import time
import random
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Thread-safe data store
data_store = {}
data_lock = threading.Lock()

# Configuration from environment variables
PORT = int(os.getenv('PORT', 5000))
WRITE_QUORUM = int(os.getenv('WRITE_QUORUM', 3))
MIN_DELAY = float(os.getenv('MIN_DELAY', 0.0))
MAX_DELAY = float(os.getenv('MAX_DELAY', 1.0))
FOLLOWER_URLS = os.getenv('FOLLOWER_URLS', '').split(',')

logger.info(f"Leader configuration:")
logger.info(f"  Port: {PORT}")
logger.info(f"  Write Quorum: {WRITE_QUORUM}")
logger.info(f"  Replication Delay: [{MIN_DELAY}s, {MAX_DELAY}s]")
logger.info(f"  Followers: {len(FOLLOWER_URLS)}")


def replicate_to_follower(follower_url, key, value, version):
    """
    Replicate a key-value pair to a single follower with simulated network delay
    
    Args:
        follower_url: URL of the follower
        key: Key to replicate
        value: Value to replicate
        version: Version number for the key-value pair
        
    Returns:
        Tuple of (success: bool, follower_url: str)
    """
    try:
        # Simulate network lag
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        time.sleep(delay)
        
        response = requests.post(
            f"{follower_url}/replicate",
            json={"key": key, "value": value, "version": version},
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully replicated {key} to {follower_url} (delay: {delay:.4f}s)")
            return (True, follower_url)
        else:
            logger.warning(f"Failed to replicate {key} to {follower_url}: {response.status_code}")
            return (False, follower_url)
            
    except Exception as e:
        logger.error(f"Error replicating to {follower_url}: {str(e)}")
        return (False, follower_url)


def replicate_to_followers(key, value, version):
    """
    Replicate to all followers concurrently and wait for write quorum
    
    Args:
        key: Key to replicate
        value: Value to replicate
        version: Version number
        
    Returns:
        Tuple of (success: bool, successful_count: int, total_count: int)
    """
    if not FOLLOWER_URLS or FOLLOWER_URLS == ['']:
        logger.warning("No followers configured")
        return (True, 0, 0)
    
    start_time = time.time()
    successful_replications = 0
    
    # Use ThreadPoolExecutor for concurrent replication
    with ThreadPoolExecutor(max_workers=len(FOLLOWER_URLS)) as executor:
        # Submit all replication tasks
        futures = {
            executor.submit(replicate_to_follower, url, key, value, version): url 
            for url in FOLLOWER_URLS if url
        }
        
        # Wait for results
        for future in as_completed(futures):
            success, follower_url = future.result()
            if success:
                successful_replications += 1
                
                # Check if we've reached the write quorum
                if successful_replications >= WRITE_QUORUM:
                    elapsed = time.time() - start_time
                    logger.info(f"Write quorum ({WRITE_QUORUM}) reached for key '{key}' in {elapsed:.4f}s")
                    return (True, successful_replications, len(FOLLOWER_URLS))
    
    elapsed = time.time() - start_time
    logger.warning(
        f"Write quorum not met for key '{key}': {successful_replications}/{WRITE_QUORUM} "
        f"(total followers: {len(FOLLOWER_URLS)}, time: {elapsed:.4f}s)"
    )
    
    return (False, successful_replications, len(FOLLOWER_URLS))


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "node_type": "leader",
        "write_quorum": WRITE_QUORUM,
        "followers": len([url for url in FOLLOWER_URLS if url])
    }), 200


@app.route('/write', methods=['POST'])
def write():
    """
    Write endpoint - only available on leader
    Implements semi-synchronous replication with write quorum
    """
    try:
        data = request.get_json()
        if not data or 'key' not in data or 'value' not in data:
            return jsonify({"error": "Missing key or value"}), 400
        
        key = data['key']
        value = data['value']
        
        start_time = time.time()
        
        # Write to leader's data store with versioning
        with data_lock:
            # Get current version and increment
            current_entry = data_store.get(key, {"version": 0})
            new_version = current_entry.get("version", 0) + 1
            
            data_store[key] = {
                "value": value,
                "version": new_version,
                "timestamp": time.time()
            }
            
            logger.info(f"Leader: Wrote key '{key}' with value '{value}' (version {new_version})")
        
        # Replicate to followers (semi-synchronous)
        success, ack_count, total_followers = replicate_to_followers(key, value, new_version)
        
        elapsed = time.time() - start_time
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Write successful with quorum {ack_count}/{total_followers}",
                "key": key,
                "value": value,
                "version": new_version,
                "latency_ms": round(elapsed * 1000, 2),
                "acknowledged_by": ack_count,
                "total_followers": total_followers
            }), 200
        else:
            # Write is in leader but quorum not met
            return jsonify({
                "status": "partial_success",
                "message": f"Write saved but quorum not met: {ack_count}/{WRITE_QUORUM}",
                "key": key,
                "value": value,
                "version": new_version,
                "latency_ms": round(elapsed * 1000, 2),
                "acknowledged_by": ack_count,
                "total_followers": total_followers
            }), 202
            
    except Exception as e:
        logger.error(f"Error in write: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/read', methods=['GET'])
def read():
    """Read endpoint - returns value for a given key"""
    try:
        key = request.args.get('key')
        if not key:
            return jsonify({"error": "Missing key parameter"}), 400
        
        with data_lock:
            if key in data_store:
                entry = data_store[key]
                return jsonify({
                    "key": key,
                    "value": entry["value"],
                    "version": entry["version"],
                    "timestamp": entry["timestamp"]
                }), 200
            else:
                return jsonify({"error": f"Key '{key}' not found"}), 404
                
    except Exception as e:
        logger.error(f"Error in read: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/data', methods=['GET'])
def get_data():
    """Get all data from the store"""
    with data_lock:
        return jsonify({
            "node_type": "leader",
            "data": data_store,
            "count": len(data_store)
        }), 200


if __name__ == '__main__':
    logger.info(f"Starting leader node on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, threaded=True)
