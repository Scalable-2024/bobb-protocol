import csv
from flask import request, g
from src.helpers.response_helper import create_response
import os
import json

def handshake():
    # Retrieve JSON data from the request body
    handshake_data = request.json

    # Retrieve IP address from g.bobb_header, assuming it's stored under 'source_ipv6'
    bobb_header = g.bobb_header
    
    source_ip = bobb_header["source_ipv6"]

    # Extract necessary fields from the handshake data
    satellite_function = handshake_data.get("satellite_function")
    public_key = handshake_data.get("public_key")
    connected_nodes = handshake_data.get("connected_nodes", [])

    # Check if required fields are present
    if not satellite_function or not public_key:
        return create_response({"error": "Missing required fields in handshake data"}, 400)

    # Append the data to the CSV file
    write_to_csv(source_ip, satellite_function, public_key, connected_nodes)

    return create_response({"message": "Neighbor added successfully"}, 200)

def write_to_csv(source_ip, satellite_function, public_key, connected_nodes):
    # Ensure the CSV file exists, creating headers if not
    port = os.getenv("PORT")
    base_dir = os.getcwd()
    directory_path = os.path.join(base_dir, "resources", "satellite_neighbours")
    file_name = os.path.join(directory_path, f"neighbours_{port}.csv")
    os.makedirs(directory_path, exist_ok=True)

    file_exists = os.path.isfile(file_name)

    with open(file_name, mode="a", newline="") as csv_file:
        fieldnames = ["ip", "function", "public_key", "connected_nodes"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        # Write the row with connected nodes as a JSON string
        writer.writerow({
            "source_ip": source_ip,
            "satellite_function": satellite_function,
            "public_key": public_key,
            "connected_nodes": json.dumps(connected_nodes)
        })
