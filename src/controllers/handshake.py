import csv
import json
import os
from flask import request, g
from src.helpers.response_helper import create_response

def handshake():
    # Retrieve JSON data from the request body
    handshake_data = request.json

    # Retrieve IP address from g.bobb_header, assuming it's stored under 'source_ipv6'
    bobb_header = g.bobb_header
    source_ip = bobb_header["source_ipv6"]

    # Extract necessary fields from the handshake data
    satellite_function = handshake_data.get("satellite_function")
    public_key = handshake_data.get("public_key")
    port = handshake_data.get("port")
    connected_nodes = handshake_data.get("connected_nodes", [])

    # Check if required fields are present
    if not satellite_function or not public_key or port is None:
        return create_response({"error": "Missing required fields in handshake data"}, 400)

    # Append the data to the CSV file if it's a new neighbor
    if write_to_csv(source_ip, satellite_function, public_key, port, connected_nodes):
        return create_response({"message": "Neighbor added successfully"}, 200)
    else:
        return create_response({"message": "Neighbor already exists"}, 200)

def write_to_csv(source_ip, satellite_function, public_key, port, connected_nodes):
    # Get file path for storing neighbor data
    own_port = os.getenv("PORT")
    base_dir = os.getcwd()
    directory_path = os.path.join(base_dir, "resources", "satellite_neighbours")
    file_name = os.path.join(directory_path, f"neighbours_{own_port}.csv")
    os.makedirs(directory_path, exist_ok=True)

    # Check if the neighbor (source_ip, port) combination already exists
    if os.path.isfile(file_name):
        with open(file_name, mode="r", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row["ip"] == source_ip and row["port"] == str(port):
                    return False  # Neighbor already exists

    # Append the new neighbor entry if it does not exist
    with open(file_name, mode="a", newline="") as csv_file:
        fieldnames = ["ip", "function", "public_key", "port", "connected_nodes"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # Write headers if file is newly created
        if csv_file.tell() == 0:
            writer.writeheader()

        # Write the row with connected nodes as a JSON string
        writer.writerow({
            "ip": source_ip,
            "function": satellite_function,
            "public_key": public_key,
            "port": port,
            "connected_nodes": json.dumps(connected_nodes)
        })

    return True
