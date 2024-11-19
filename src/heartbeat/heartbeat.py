import json
import os
import sys
from flask import Flask, request, jsonify
import requests
import threading
import time

from src.config.constants import MAX_TIMEOUT, X_BOBB_HEADER
from src.routing.route_generator import create_routing_tables
from src.utils.headers.necessary_headers import BobbHeaders

app = Flask(__name__)

# Load configuration file dynamically
our_port = os.getenv("PORT")
our_ip = os.getenv("IP")

proxies = {
  'http': '',
  'https': '',
}

# ******** Remove THIS WHEN ACTUALLY RUNNING *****
# our_port = 33001
# our_ip = "192.168.0.235" 

neighbours_file = f'resources/satellite_neighbours/neighbours_{our_port}.json'

def safe_load_json(file_path):
    """
    Safely load JSON data from a file.
    If the file is empty or contains invalid JSON, return an empty dictionary.
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def safe_save_json(file_path, data):
    """
    Safely save JSON data to a file, creating directories if necessary.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


def update_last_contact(ip, port):
    """
    Updates the last_contact time for the given neighbor (identified by IP and port)
    in the neighbours_<our_port>.json file.
    """
    neighbours_data = safe_load_json(neighbours_file)
    
    for neighbour in neighbours_data:
        if neighbour['ip'] == ip and neighbour['port'] == port:
            neighbour['last_contact'] = int(time.time())
            break
    
    safe_save_json(neighbours_file, neighbours_data)

def heartbeat():
    received_constellation = request.json.get("constellation", {}) if request.json else {}
    
    # Load our existing constellation data
    constellation_file = f'resources/satellite_constellation_set/constellation_{our_port}.json'
    try:
        with open(constellation_file, 'r') as f:
            our_constellation = json.load(f)
            f.close()
    except (FileNotFoundError, json.JSONDecodeError):
        our_constellation = {}
    
    # Update constellation data based on received information
    for node_id, node_data in received_constellation.items():
        # If node doesn't exist in our constellation, add it
        if node_id not in our_constellation:
            our_constellation[node_id] = node_data
        # If node exists and received data is fresher
        elif node_data['freshness'] > our_constellation[node_id]['freshness']:
            # Compare neighbours data excluding freshness
            current_neighbours = our_constellation[node_id]['neighbours']
            new_neighbours = node_data['neighbours']
            
            if current_neighbours != new_neighbours:
                # Update entire node data if there are changes
                our_constellation[node_id] = node_data
            else:
                # Only update freshness if no other changes
                our_constellation[node_id]['freshness'] = node_data['freshness']
    
    # Save the updated constellation data
    safe_save_json(constellation_file, our_constellation)

    try:
        create_routing_tables()
    except Exception as e:
        print(f"Error creating routing tables: {e}")
        
    return jsonify({"message": "Constellation data processed"}), 200


def send_heartbeat_to_neighbours():
    # Load neighbours from the JSON file
    try:
        with open(neighbours_file) as f:
            raw_neighbours = json.load(f)
    except FileNotFoundError:
        return # If no neighbours, we don't care
    
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
            neighbour_urls.add(f'https://{neighbour["ip"]}:{neighbour["port"]}/heartbeat')
            # neighbour_urls.add(f'https://192.168.0.235:{neighbour["port"]}/heartbeat')
    
    # print(f"Neighbours : {neighbours}")
    # print(f'Neighbours urls: {neighbour_urls}')
    
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
        safe_save_json(constellation_file, satellite_data)
        
        # Assign the initial data to constellation_data
        constellation_data = satellite_data
    else:
        # File exists, read the existing data
        constellation_data = safe_load_json(constellation_file)
        
        # Our satellite ID
        satellite_id = f"{our_ip}:{our_port}"
        current_time = int(time.time())

        # Update our satellite's neighbours
        constellation_data[satellite_id] = {
            "freshness": current_time,
            "neighbours": neighbours
        }

        # Write the updated constellation data back to the JSON file
        safe_save_json(constellation_file, constellation_data)
                
    # Send POST requests to all neighbour URLs
    for url in neighbour_urls:
        try:            
            header = BobbHeaders(message_type=1, source_ipv4=our_ip,
                         source_port=int(our_port)).build_header().hex()
            headers = {
                X_BOBB_HEADER: header,
            }

            # Send handshake
            response = requests.post(
                url, 
                verify=False,  # Already set
                timeout=3,
                proxies=proxies,
                headers=headers,
                json={"constellation": constellation_data},
                allow_redirects=True
            )
            
            # response = requests.post(url, json={"constellation": constellation_data})
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

