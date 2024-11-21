# Written by Claire, modified by Patrick
import time
from src.utils.handshake_body import SatelliteHandshake
from src.utils.headers.necessary_headers import BobbHeaders
from src.config.constants import X_BOBB_HEADER
from src.helpers.response_helper import create_response
import json
import os


def create_handshake_message(name, device_function, public_key, port, ip):
    handshake_body = SatelliteHandshake(
        name, device_function, public_key, port).build_message()
    header = BobbHeaders(message_type=1, source_ipv4=ip,
                         source_port=port).build_header().hex()
    headers = {
        X_BOBB_HEADER: header,
    }
    return handshake_body, headers


def write_received_handshake(handshake_data, bobb_header):
    try:
        handshake_data = json.loads(handshake_data)
    except TypeError:
        handshake_data = handshake_data
    except json.JSONDecodeError as e:
        return create_response({"error": f"Failed to parse JSON: {str(e)}"}, 400)

    # Retrieve IP address from g.bobb_header, assuming it's stored under 'source_ipv4'
    source_ip = bobb_header["source_ipv4"]

    # Extract necessary fields from the handshake data

    device_function = handshake_data["device_function"]
    public_key = handshake_data["public_key"]
    source_port = handshake_data["port"]
    timestamp = handshake_data["timestamp"]

    # Check if required fields are present
    if device_function is None or public_key is None or source_port is None:
        return create_response({"error": "Missing required fields in handshake data"}, 400)

    # Append the data to the JSON file if it's a new neighbor (set the last contact time to the current time for this neighbour)
    if write_to_json(source_ip, device_function, public_key, source_port, timestamp):
        print(f"Neighbour {source_ip}:{source_port} added")


def write_to_json(source_ip, device_function, public_key, port, timestamp):
    # Get file path for storing neighbor data
    own_port = os.getenv("PORT")
    base_dir = os.getcwd()
    directory_path = os.path.join(
        base_dir, "resources", "satellite_neighbours")
    file_name = os.path.join(directory_path, f"neighbours_{own_port}.json")
    os.makedirs(directory_path, exist_ok=True)

    # Load existing data if the JSON file exists
    if os.path.isfile(file_name):
        with open(file_name, "r") as json_file:
            try:
                neighbors = json.load(json_file)
            except json.JSONDecodeError:
                # Reset neighbors if file is corrupted
                neighbors = []
    else:
        neighbors = []

    # Check if the neighbor (source_ip, port) combination already exists
    for neighbor in neighbors:
        if neighbor["ip"] == source_ip and neighbor["port"] == port:
            return False  # Neighbor already exists

    # Flexible validation for required fields
    if source_ip is None or port is None:
        print("Error: Missing required fields in neighbour.")
        return False

    # Create a new neighbor entry
    new_neighbor = {
        "ip": source_ip,
        "function": device_function,  # Allow "undefined"
        "public_key": public_key,        # Allow empty string
        "port": port,
        "last_contact": timestamp
    }

    # Append the new neighbor and save back to JSON
    neighbors.append(new_neighbor)

    with open(file_name, "w") as json_file:
        json.dump(neighbors, json_file, indent=4)

    return True
