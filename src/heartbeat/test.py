import json
import os
import sys
from flask import Flask, request, jsonify
import requests
import threading
import time

app = Flask(__name__)

# Load configuration file dynamically
our_port = os.getenv("PORT")

# ******** Remove THIS WHEN ACTUALLY RUNNING *****
our_port = 33002
our_ip = "192.168.0.235" 

neighbours_file = f'resources/satellite_neighbours/neighbours_{our_port}.json'

MAX_TIMEOUT = 30  # Set the maximum timeout of a neighbor to 30 seconds


def update_last_contact(ip, port):
    """
    Updates the last_contact time for the given neighbor (identified by IP and port)
    in the neighbours_<our_port>.json file.
    """
    with open(neighbours_file, 'r') as f:
        neighbours_data = json.load(f)
    
    for neighbour in neighbours_data:
        if neighbour['ip'] == ip and neighbour['port'] == port:
            neighbour['last_contact'] = int(time.time())
            break
    
    with open(neighbours_file, 'w') as f:
        json.dump(neighbours_data, f, indent=4)


@app.route("/heartbeat", methods=["POST"])
def receive_heartbeat():
    print("Heartbeat received")
    return jsonify({"message": "Heartbeat received"}), 200


def send_heartbeat_to_neighbours():
    while True:
        # Load neighbours from the JSON file
        with open(neighbours_file) as f:
            raw_neighbours = json.load(f)
        
        # Initialize neighbours dictionary from the provided JSON format
        neighbours = {}
        current_time = int(time.time())
        neighbour_urls = set()
        for neighbour in raw_neighbours:
            if current_time - neighbour['last_contact'] <= MAX_TIMEOUT:  # Keep valid neighbors
                neighbour_id = f"{neighbour['ip']}:{neighbour['port']}"
                neighbours[neighbour_id] = {
                    "ip": neighbour["ip"],
                    "port": neighbour["port"],
                    "public_key": neighbour["public_key"],
                    "function": neighbour["function"],
                    "last_contact": neighbour["last_contact"],
                }
                neighbour_urls.add(f'http://{neighbour["ip"]}:{neighbour["port"]}/heartbeat')
        
        print(f"Neighbours : {neighbours}")
        print(f'Neighbours urls: {neighbour_urls}')
        
        # Define directory and file paths
        constellation_dir = 'resources/satellite_constellation_set'
        constellation_file = f'{constellation_dir}/constellation_{our_port}.json'
        
        # Check if directory exists, if not create it
        if not os.path.exists(constellation_dir):
            os.makedirs(constellation_dir)
        
        # Check if the constellation JSON file exists
        if not os.path.exists(constellation_file):
            # Create the initial data structure
            satellite_id = f"{our_ip}:{our_port}"
            current_time = int(time.time())
            # Our satellite data
            satellite_data = {
                satellite_id: {
                    "freshness": current_time,
                    "neighbours": list(neighbours.values())
                }
            }
            # Write to the file
            with open(constellation_file, 'w') as f:
                json.dump(satellite_data, f, indent=4)
        else:
            print('file exists !!!')
            # File exists, read the existing data
            with open(constellation_file, 'r') as f:
                constellation_data = json.load(f)
            
            # Our satellite ID
            satellite_id = f"{our_ip}:{our_port}"
            current_time = int(time.time())
            
            # Update our satellite's neighbours
            constellation_data[satellite_id] = {
                "freshness": current_time,
                "neighbours": neighbours
            }
            
            # Write the updated constellation data back to the JSON file
            with open(constellation_file, 'w') as f:
                json.dump(constellation_data, f, indent=4)
                
        # Send POST requests to all neighbour URLs
        for url in neighbour_urls:
            try:
                response = requests.post(url, json={"neighbours": neighbours})
                if response.status_code == 200:
                    print(f"Heartbeat sent successfully to {url}")
                    
                    # Parse the IP and port from the URL
                    url_components = url.split(':')
                    neighbour_ip = url_components[1].replace('//', '')
                    neighbour_port = int(url_components[2].split('/')[0])
                    
                    # Update last_contact for this neighbour
                    update_last_contact(neighbour_ip, neighbour_port)
                else:
                    print(f"Failed to send heartbeat to {url}. Status code: {response.status_code}")
            except requests.RequestException as e:
                print(f"Error sending heartbeat to {url}: {e}")

        # Sleep for 10 seconds before the next heartbeat
        time.sleep(10)


if __name__ == "__main__":
    # Start the send_heartbeat function in a separate thread
    heartbeat_thread = threading.Thread(target=send_heartbeat_to_neighbours, daemon=True)
    heartbeat_thread.start()

    # Run the Flask app
    app.run(host='0.0.0.0', port=our_port)
