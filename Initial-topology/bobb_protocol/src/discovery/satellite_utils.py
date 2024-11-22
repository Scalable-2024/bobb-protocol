# bobb_protocol/src/discovery/satellite_utils.py
import requests
import subprocess
import re
import platform

# Written by Yuchen
"""
    This script provides utility functions for interacting with satellites in the network.
"""
def fetch_satellite_state(ip, port, verbose=False):
    """Fetch the state of the satellite from the /id endpoint."""
    try:
        url = f"https://{ip}:{port}/id"
        if verbose:
            print(f"Fetching state from URL: {url}")

        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()

        # Directly extract latency and load
        latency = data.get("latency")
        load = data.get("load")
        if verbose:
            print(f"Latency: {latency}, Load: {load}")

        # Return the state
        return {
            "latency": latency,
            "load": load
        }
    except requests.RequestException as e:
        if verbose:
            print(f"Error fetching state from {url}: {e}")
    return None

def remove_offline_satellites(topology, config):
    """Remove satellites that are offline."""
    current_nodes = list(topology.nodes())
    nodes_to_remove = []

    for node in current_nodes:
        ip, port = node.split(":")
        state = fetch_satellite_state(ip, port)
        if not state:  # Satellite is offline
            print(f"Satellite {node} is offline, removing...")
            nodes_to_remove.append(node)

    for node in nodes_to_remove:
        topology.remove_node(node)

    return topology

def update_satellite_status(topology, config):
    """Update the status (latency/load) of satellites in the topology."""
    for satellite in config['satellites']:
        ip = satellite['ip']
        port = satellite['port']
        node = f"{ip}:{port}"

        # if the node is not in the topology, add it
        if node not in topology:
            print(f"Node {node} not in topology. Adding it.")
            topology.add_node(node, latency=None, load=None)

        # get the current state of the satellite
        state = fetch_satellite_state(ip, port)
        if state:
            latency = state.get("latency")
            load = state.get("load")
            if latency is not None:
                topology.nodes[node]["latency"] = latency
            if load is not None:
                topology.nodes[node]["load"] = load
    return topology

def ping_with_response_time(ipv4, timeout=5):
    """Ping an IPv4 address and return the response time in ms."""
    try:
        # Determine the ping command based on the operating system
        if platform.system().lower() == "windows":
            cmd = f"ping -n 1 -w {timeout * 1000} {ipv4}"
        else:
            cmd = f"ping -c 1 -W {timeout} {ipv4}"

        # Execute the ping command
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)

        # Extract the response time from the output
        match = re.search(r'time[=<](\d+\.\d+) ms', output)
        if match:
            return float(match.group(1))
        return "N/A"
    except subprocess.CalledProcessError:
        return "N/A"  # Ping failed or timeout

def check_if_satellite(ipv4, port, endpoint="/id"):
    """Make an HTTP request using curl and return True if it is a satellite."""
    try:
        addr = f"https://{ipv4}:{port}{endpoint}"
        print(f"Attempting HTTP request to {addr}...")
        resp = requests.get(addr, verify=False, timeout=3)
        if resp.status_code == 200:
            json_data = resp.json()
            return json_data.get("data") == "I am a satellite"
        return False
    except requests.RequestException as e:
        print(f"Error connecting to {addr}: {e}")
        return False





