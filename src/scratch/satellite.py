import json
import sys
from flask import Flask, request, jsonify
from datetime import datetime
import requests
import threading
import time

app = Flask(__name__)

# Load configuration file dynamically
if len(sys.argv) < 2:
    print("Usage: python satellite.py <config_file>")
    sys.exit(1)

config_file = sys.argv[1]
with open(config_file) as f:
    config = json.load(f)
    device_id = config["id"]
    port = config["port"]

# Initialize neighbors
neighbors = {}
for neighbor in config["neighbors"]:
    neighbors[neighbor["id"]] = {
        "ip": neighbor["ip"],
        "port": neighbor["port"],
        "public_key": neighbor["public_key"],
        "last_contacted": None,
        "status": "disconnected"
    }

@app.route("/heartbeat", methods=["GET"])
def receive_heartbeat():
    sender_id = request.args.get("satellite_id")
    ip = request.args.get("ip")
    sender_port = request.args.get("port")
    
    if not sender_id or not ip or not sender_port:
        return jsonify({"error": "Missing required fields"}), 400

    neighbors[sender_id] = {
        "ip": ip,
        "port": int(sender_port),
        "last_contacted": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "status": "connected"
    }
    print("Received heartbeat from {} at {}".format(sender_id, neighbors[sender_id]["last_contacted"]))
    return jsonify({"status": "Heartbeat received", "timestamp": neighbors[sender_id]["last_contacted"]}), 200

@app.route("/neighbors", methods=["GET"])
def get_neighbors():
    return jsonify(neighbors), 200

def send_heartbeat():
    while True:
        payload = {
            "satellite_id": device_id,
            "ip": "http://127.0.0.1",
            "port": port
        }
        for neighbor_id, neighbor_data in neighbors.items():
            try:
                url = "{}:{}/heartbeat".format(neighbor_data['ip'], neighbor_data['port'])
                response = requests.get(url, params=payload, timeout=5)
                if response.status_code == 200:
                    print("Heartbeat sent to {}. Response: {}".format(neighbor_id, response.json()))
                else:
                    print("Failed to send heartbeat to {}. Status Code: {}".format(neighbor_id, response.status_code))
            except requests.RequestException as e:
                neighbors[neighbor_id]["status"] = "disconnected"
                print("Error sending heartbeat to {}: {}".format(neighbor_id, e))
        time.sleep(10)

def monitor_neighbors():
    while True:
        current_time = datetime.utcnow()
        for node_id in list(neighbors.keys()):
            if neighbors[node_id]["last_contacted"]:
                last_contacted = datetime.strptime(neighbors[node_id]["last_contacted"], '%Y-%m-%dT%H:%M:%SZ')
                if (current_time - last_contacted).total_seconds() > 30:
                    print("Node {} is inactive. Removing from neighbor table.".format(node_id))
                    del neighbors[node_id]
        time.sleep(10)

if __name__ == "__main__":
    monitor_thread = threading.Thread(target=monitor_neighbors)
    monitor_thread.setDaemon(True)
    monitor_thread.start()

    heartbeat_thread = threading.Thread(target=send_heartbeat)
    heartbeat_thread.setDaemon(True)
    heartbeat_thread.start()

    print("Starting Flask server for receiving heartbeats on port {}".format(port))
    app.run(host="0.0.0.0", port=port)
