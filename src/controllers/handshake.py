import os
import json
from flask import request, g
from src.helpers.response_helper import create_response

def handshake():
    print("About to send handshakes")
    # Retrieve JSON data from the request body
    handshake_data = request.get_json()

    print(request.content_type)
    print(f"handshake_data type: {type(handshake_data)}")
    print(f"handshake_data: {handshake_data}")

    try:
        handshake_data = json.loads(handshake_data)
    except json.JSONDecodeError as e:
        return create_response({"error": f"Failed to parse JSON: {str(e)}"}, 400)

    # Retrieve IP address from g.bobb_header, assuming it's stored under 'source_ipv4'
    bobb_header = g.bobb_header
    source_ip = bobb_header["source_ipv4"]

    # Extract necessary fields from the handshake data
    satellite_function = handshake_data["satellite_function"]
    public_key = handshake_data["public_key"]
    port = handshake_data["port"]
    connected_nodes = handshake_data["connected_nodes"]

    # Check if required fields are present
    if satellite_function is None or public_key is None or port is None:
        return create_response({"error": "Missing required fields in handshake data"}, 400)

    # Append the data to the JSON file if it's a new neighbor
    if write_to_json(source_ip, satellite_function, public_key, port, connected_nodes):
        return create_response({"message": "Neighbor added successfully"}, 200)
    else:
        return create_response({"message": "Neighbor already exists"}, 200)

def write_to_json(source_ip, satellite_function, public_key, port, connected_nodes):
    # Get file path for storing neighbor data
    own_port = os.getenv("PORT")
    base_dir = os.getcwd()
    directory_path = os.path.join(base_dir, "resources", "satellite_neighbours")
    file_name = os.path.join(directory_path, f"neighbours_{own_port}.json")
    os.makedirs(directory_path, exist_ok=True)

    # Load existing data if the JSON file exists
    if os.path.isfile(file_name):
        with open(file_name, "r") as json_file:
            neighbors = json.load(json_file)
    else:
        neighbors = []

    # Check if the neighbor (source_ip, port) combination already exists
    for neighbor in neighbors:
        if neighbor["ip"] == source_ip and neighbor["port"] == port:
            return False  # Neighbor already exists

    # Create a new neighbor entry
    new_neighbor = {
        "ip": source_ip,
        "function": satellite_function,
        "public_key": public_key,
        "port": port,
        "connected_nodes": connected_nodes
    }

    # Append the new neighbor and save back to JSON
    neighbors.append(new_neighbor)
    with open(file_name, "w") as json_file:
        json.dump(neighbors, json_file, indent=4)

    return True
