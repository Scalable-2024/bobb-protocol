# Written by Yuchen
"""
    This script simulates a satellite server that provides information about its state and neighbors.
"""
# mock_satellite.py
from flask import Flask, jsonify
import random
import argparse
import json

from comprehensive_simulation import CONFIG_FILE

app = Flask(__name__)

CONFIG_FILE = "satellites_config.json"
@app.route('/id', methods=['GET'])
def id_endpoint():
    # Simulate satellite state
    state = {
        "data": "I am a satellite",
        "latency": round(random.uniform(10, 100), 2),  # ms
        "load": random.randint(1, 100)  # load 1-100 %
    }
    return jsonify(state)

@app.route('/neighbors', methods=['GET'])
def neighbors():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        ip = app.config["satellite_ip"]
        port = app.config["satellite_port"]
        node_identity = f"{ip}:{port}"

        for satellite in config.get("satellites", []):
            if f"{satellite['ip']}:{satellite['port']}" == node_identity:
                return jsonify({"neighbors": satellite.get("neighbors", [])}), 200

        return jsonify({"error": "Satellite not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mock Satellite Server")
    parser.add_argument('--ip', type=str, required=True, help='IP address to bind')
    parser.add_argument('--port', type=int, required=True, help='Port to bind')
    args = parser.parse_args()

    app.config["satellite_ip"] = args.ip
    app.config["satellite_port"] = args.port
    print(f"Starting satellite at {args.ip}:{args.port}")
    app.run(host=args.ip, port=args.port, debug=True)

