import os
import csv
import json
import requests
from src.utils.handshake_body import SatelliteHandshake
from src.utils.headers.necessary_headers import BobbHeaders
from src.config.constants import X_BOBB_HEADER
from src.discovery.discovery import ipv4_to_ipv6

# TODO allow self signed certificates
import urllib3
urllib3.disable_warnings()

# To block the SCSS proxying, to connect directly to the other pis
proxies = {
  'http': '',
  'https': '',
}

def send_handshakes():
    known_satellites = set(get_known_satellites())
    current_neighbours = set(get_neighbours())

    new_neighbours = known_satellites - current_neighbours
    for neighbour in new_neighbours:
        send_handshake(neighbour)


def send_handshake(neighbour):
    n_ip, n_port = neighbour
    satellite_function = "undefined" # Replace for each groups code
    public_key = "" # TODO add public key here
    ip = ipv4_to_ipv6(os.getenv("IP"))
    port = int(os.getenv("PORT"))
    connected_nodes = [] # Currently not allowing recursive nodes

    handshake_body = SatelliteHandshake(satellite_function, public_key, port, connected_nodes).build_message()
    header = BobbHeaders(message_type=1, source_ipv6=ip, source_port=port).build_header().hex()
    headers = {
        X_BOBB_HEADER: header,
    }

    resp = requests.post(f"https://{n_ip}:{n_port}/handshake", verify=False, timeout=3, proxies=proxies, headers=headers, json=handshake_body)
    print(f"Handshake response: {resp.status_code}, {resp.text}")

    return
    
def get_known_satellites():
    ip_port_pairs = []

    port = os.getenv("PORT")
    base_dir = os.getcwd()
    directory_path = os.path.join(base_dir, "resources", "satellite_listings")
    file_name = os.path.join(directory_path, f"full_satellite_listing_{port}.csv")
    
    with open(file_name, mode="r", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            # Extract the IP and Port values
            ipv4 = row.get("IPv4")
            port = row.get("Port")
            
            # Add IPv4 and Port if both are present
            if ipv4 and port:
                ip_port_pairs.append((ipv4, port))
    
    return ip_port_pairs

def get_neighbours():
    # Get file path for reading neighbor data
    own_port = os.getenv("PORT")
    base_dir = os.getcwd()
    file_name = os.path.join(base_dir, "resources", "satellite_neighbours", f"neighbours_{own_port}.json")
    
    # Check if file exists
    if not os.path.isfile(file_name):
        return []  # Return an empty list if the file doesn't exist

    # Load the JSON data
    with open(file_name, "r") as json_file:
        neighbors = json.load(json_file)

    # Extract (ip, port) combinations
    ip_port_combinations = [(neighbor["ip"], neighbor["port"]) for neighbor in neighbors]

    return ip_port_combinations



