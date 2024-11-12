import json
from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time
import requests

app = Flask(__name__)

# In-memory table to store neighbors and their respective neighbors
neighbor_table = {}

# Define timeout duration for heartbeat monitoring (in seconds)
HEARTBEAT_TIMEOUT = 30

@app.route("/heartbeat", methods=["GET"])
def receive_heartbeat():
    satellite_id = request.args.get("satellite_id")
    ip = request.args.get("ip")
    port = request.args.get("port")
    
    if not satellite_id or not ip or not port:
        return jsonify({"error": "Missing required fields"}), 400

    # Update or add the node to the neighbor table
    neighbor_table[satellite_id] = {
        "ip": ip,
        "port": int(port),
        "last_contacted": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "status": "connected"
    }
    print("Received heartbeat from {} at {}".format(satellite_id, neighbor_table[satellite_id]["last_contacted"]))
    return jsonify({"status": "Heartbeat received", "timestamp": neighbor_table[satellite_id]["last_contacted"]}), 200

@app.route("/neighbors", methods=["GET"])
def get_neighbors():
    return jsonify(neighbor_table), 200

def send_heartbeat():
    while True:
        payload = {
            "satellite_id": device_id,
            "ip": "http://127.0.0.1",
            "port": port
        }
        for neighbor_id, neighbor_data in neighbor_table.items():
            try:
                url = "{}:{}/heartbeat".format(neighbor_data['ip'], neighbor_data['port'])
                response = requests.get(url, params=payload, timeout=5)
                if response.status_code == 200:
                    print("Heartbeat sent to {}. Response: {}".format(neighbor_id, response.json()))
                else:
                    print("Failed to send heartbeat to {}. Status Code: {}".format(neighbor_id, response.status_code))
            except requests.RequestException as e:
                neighbor_table[neighbor_id]["status"] = "disconnected"
                print("Error sending heartbeat to {}: {}".format(neighbor_id, e))
        time.sleep(10)

def monitor_neighbors():
    while True:
        current_time = datetime.utcnow()
        for node_id in list(neighbor_table.keys()):
            if neighbor_table[node_id]["last_contacted"]:
                last_contacted = datetime.strptime(neighbor_table[node_id]["last_contacted"], '%Y-%m-%dT%H:%M:%SZ')
                if (current_time - last_contacted).total_seconds() > HEARTBEAT_TIMEOUT:
                    print("Node {} is inactive. Removing from neighbor table.".format(node_id))
                    del neighbor_table[node_id]
        time.sleep(10)

if __name__ == "__main__":
    device_id = "BASE_STATION"
    port = 5000  # Set the base station to listen on port XXXX

    # Start monitoring and heartbeat threads
    monitor_thread = threading.Thread(target=monitor_neighbors)
    monitor_thread.setDaemon(True)
    monitor_thread.start()

    heartbeat_thread = threading.Thread(target=send_heartbeat)
    heartbeat_thread.setDaemon(True)
    heartbeat_thread.start()

    print("Starting Flask server for receiving heartbeats on port {}".format(port))
    app.run(host="0.0.0.0", port=port)
