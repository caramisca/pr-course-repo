"""
Follower Node for Distributed Key-Value Store
Receives replicated data from leader and handles read requests concurrently
"""

import os
import time
import logging
import threading
from flask import Flask, request, jsonify

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
NODE_ID = os.getenv('NODE_ID', 'follower')

logger.info(f"Follower configuration:")
logger.info(f"  Node ID: {NODE_ID}")
logger.info(f"  Port: {PORT}")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    with data_lock:
        key_count = len(data_store)
    
    return jsonify({
        "status": "healthy",
        "node_type": "follower",
        "node_id": NODE_ID,
        "keys_stored": key_count
    }), 200


@app.route('/replicate', methods=['POST'])
def replicate():
    """
    Replication endpoint - receives replicated data from leader
    Implements versioning to handle concurrent writes
    """
    try:
        data = request.get_json()
        if not data or 'key' not in data or 'value' not in data:
            return jsonify({"error": "Missing key or value"}), 400
        
        key = data['key']
        value = data['value']
        version = data.get('version', 1)
        
        # Apply replication with version checking
        with data_lock:
            current_entry = data_store.get(key)
            
            # Only apply if version is newer or key doesn't exist
            if current_entry is None or version > current_entry.get("version", 0):
                data_store[key] = {
                    "value": value,
                    "version": version,
                    "timestamp": time.time()
                }
                logger.info(
                    f"{NODE_ID}: Replicated key '{key}' with value '{value}' "
                    f"(version {version})"
                )
                action = "updated"
            else:
                logger.info(
                    f"{NODE_ID}: Ignored replication for key '{key}' "
                    f"(version {version} <= current {current_entry.get('version', 0)})"
                )
                action = "ignored"
        
        return jsonify({
            "status": "success",
            "message": f"Replication {action}",
            "node_id": NODE_ID,
            "key": key,
            "version": version
        }), 200
        
    except Exception as e:
        logger.error(f"{NODE_ID}: Error in replicate: {str(e)}")
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
                    "node_id": NODE_ID,
                    "key": key,
                    "value": entry["value"],
                    "version": entry["version"],
                    "timestamp": entry["timestamp"]
                }), 200
            else:
                return jsonify({"error": f"Key '{key}' not found"}), 404
                
    except Exception as e:
        logger.error(f"{NODE_ID}: Error in read: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/data', methods=['GET'])
def get_data():
    """Get all data from the store"""
    with data_lock:
        return jsonify({
            "node_type": "follower",
            "node_id": NODE_ID,
            "data": data_store,
            "count": len(data_store)
        }), 200


if __name__ == '__main__':
    logger.info(f"Starting follower node '{NODE_ID}' on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, threaded=True)
