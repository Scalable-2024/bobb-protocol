import json
import os
import sys
from flask import Flask, request, jsonify
from datetime import datetime
import requests
import threading
import time

app = Flask(__name__)

# Load configuration file dynamically
our_port = os.getenv("PORT")

# ******** Remove THIS WHEN ACTUALLY RUNNING *****
our_port = 33001
our_ip = "192.168.0.235" 

neighbours_file = f'resources/satellite_neighbours/neighbours_{our_port}.json'

# Load neighbors from the JSON file
with open(neighbours_file) as f:
    raw_neighbors = json.load(f)

# Initialize neighbors dictionary from the provided JSON format
neighbors = {}
for neighbor in raw_neighbors:
    neighbor_id = f"{neighbor['ip']}:{neighbor['port']}"
    neighbors[neighbor_id] = {
        "ip": neighbor["ip"],
        "port": neighbor["port"],
        "public_key": neighbor["public_key"],
        "function": neighbor["function"],
        "last_contacted": datetime.utcnow(),
    }

def find_neighbor(raw_neighbors_list, ip, port):
    """
    Helper function to find a neighbor in the raw_neighbors list by IP and port.
    Returns the neighbor dictionary if found, else None.
    """
    for neighbor in raw_neighbors_list:
        if neighbor['ip'] == ip and neighbor['port'] == port:
            return neighbor
    return None

@app.route("/heartbeat", methods=["POST"])
def receive_heartbeat():
    print()


def send_heartbeat():
    while True:
        # print("Sending heartbeat...")
        print(f"Neighbours: {neighbors}")
        time.sleep(10)


if __name__ == "__main__":
    # Start the send_heartbeat function in a separate thread
    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()

    # Run the Flask app
    app.run(host='0.0.0.0', port=our_port)
