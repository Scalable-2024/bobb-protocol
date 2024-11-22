# bobb_protocol/src/discovery/discovery.py Written by Claire, modified by Yuchen
import argparse
import json
import random
import requests
import networkx as nx
import urllib3
import matplotlib.pyplot as plt # if running on the raspberry pi, command this line
from typing import Dict, Union
from bobb_protocol.src.discovery.satellite_utils import ping_with_response_time, check_if_satellite, fetch_satellite_state

# Disable SSL warnings
urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    'http': '',
    'https': '',
}

def get_neighbors(ipv4, port, endpoint="/neighbors", verbose=False):
    """
    Make an HTTP request to fetch the neighbors of a satellite.
    Return a list of neighbors if successful, else an empty list.
    """
    try:
        # construct the address
        addr = f"https://{ipv4}:{port}{endpoint}"
        if verbose:
            print(f"Attempting HTTP request to {addr}...")

        # request the target address
        resp = requests.get(addr, verify=False, timeout=3)

        # check the HTTP status code and response
        if resp.status_code == 200:
            if verbose:
                print(f"HTTP 200 OK from {addr}")
            json_data = resp.json()
            # 返回 neighbors 列表
            return json_data.get("neighbors", [])
        return []
    except Exception as e:
        if verbose:
            print(f"Error connecting to {addr}: {e}")
        return []

def ipv4_to_ipv6(ipv4: str) -> str:
    """Convert an IPv4 address to IPv6 using the ::ffff: method."""
    return "::ffff:{}".format(ipv4)

def discover_satellites(config_file: str, endpoint1: str = "/id", endpoint2: str = "/neighbors") -> Dict[str, Dict]:
    """Discover satellites based on a configuration file."""
    discovered = {}
    with open(config_file, 'r') as f:
        config = json.load(f)

    for satellite in config.get("satellites", []):
        ip = satellite.get("ip")
        port = satellite.get("port")
        if not ip or not port:
            print(f"Skipping satellite entry with missing IP or port: {satellite}")
            continue

        # Measure response time
        response_time = ping_with_response_time(ip)

        # Check if it is a satellite
        is_satellite = check_if_satellite(ip, port, endpoint1)

        # Get neighbors
        neighbors = get_neighbors(ip, port, endpoint2)
        if neighbors is None:
            neighbors = []

        discovered[f"{ip}:{port}"] = {
            "ipv4": ip,
            "ipv6": ipv4_to_ipv6(ip),
            "response time (ms)": response_time if response_time is not None else "N/A",
            "is a satellite?": is_satellite,
            "neighbors": neighbors
        }

    return discovered


def build_topology(satellites: Dict[str, Dict], latency_weight=0.7, load_weight=0.3) -> nx.Graph:
    """
    Build the network topology based on discovered satellites.

    Args:
        satellites (Dict): Satellite information.
        latency_weight (float): Weight for latency in the edge calculation (default=0.7).
        load_weight (float): Weight for load in the edge calculation (default=0.3).

    Returns:
        nx.Graph: The constructed network topology.
    """
    topology = nx.Graph()

    # Add nodes
    for ip, info in satellites.items():
        # Dynamically fetch latency and load
        satellite_ip = ip.split(":")[0]
        satellite_port = int(ip.split(":")[1])  # Ensure the port is an integer
        state = fetch_satellite_state(satellite_ip, satellite_port)

        # Set latency and load with fallback to reasonable defaults
        latency = state.get("latency") if state else 100.0  # Default to 100ms
        load = state.get("load") if state else 1.0  # Default to maximum load (1.0)

        # Add the node to the topology
        topology.add_node(
            ip,
            latency=latency,
            load=load,
            is_satellite=info.get("is a satellite?", False)
        )

    # Add edges based on neighbors
    for ip, info in satellites.items():
        for neighbor in info.get("neighbors", []):  # Ensure neighbors exist
            if neighbor in satellites:
                # Fetch latencies and loads for both the current node and its neighbor
                latency1 = topology.nodes[ip].get("latency", 100.0)  # Default 100ms
                load1 = topology.nodes[ip].get("load", 1.0)  # Default maximum load
                latency2 = topology.nodes[neighbor].get("latency", 100.0)
                load2 = topology.nodes[neighbor].get("load", 1.0)

                # Calculate the combined weight based on latency and load
                weight = (
                        (latency_weight * ((latency1 + latency2) / 2)) +  # Average latency
                        (load_weight * ((load1 + load2) / 2))  # Average load
                )

                # Add the edge with the calculated weight
                topology.add_edge(ip, neighbor, weight=round(weight, 4))  # 4 decimal points

    return topology

def visualize_topology(topology: nx.Graph, interval):
    """Visualize the satellite topology graph."""
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(topology)
    nx.draw(topology, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10)

    # Show edge weights
    edge_labels = nx.get_edge_attributes(topology, "weight")
    nx.draw_networkx_edge_labels(topology, pos, edge_labels=edge_labels)

    plt.title("Network Topology with Weights")
    plt.pause(interval)
    plt.close()

def calculate_weight(latency1, latency2, load1, load2, latency_weight=0.7, load_weight=0.3):
    """
    Calculate the edge weight based on latency and load.

    Args:
        latency1 (float): Latency of the first node.
        latency2 (float): Latency of the second node.
        load1 (float): Load of the first node.
        load2 (float): Load of the second node.
        latency_weight (float): Weight given to latency (default=0.7).
        load_weight (float): Weight given to load (default=0.3).

    Returns:
        float: The calculated weight.
    """
    # Set default values for None types
    if latency1 is None:
        latency1 = 100.0  # Default latency
    if latency2 is None:
        latency2 = 100.0  # Default latency
    if load1 is None:
        load1 = 1.0  # Default maximum load
    if load2 is None:
        load2 = 1.0  # Default maximum load

    # Calculate average latency and load
    average_latency = (latency1 + latency2) / 2
    average_load = (load1 + load2) / 2

    # Calculate total weight
    weight = (latency_weight * average_latency) + (load_weight * average_load)
    return round(weight, 4)  # Return rounded weight

def update_topology(topology, changes):
    """
    Update the topology based on incremental changes and dynamically fetch latency/load.
    """
    def add_or_update_node(node, ipv4, port):
        """Helper function to add or update a node's latency and load."""
        state = fetch_satellite_state(ipv4, port)
        latency = state.get("latency", 100.0) if state else 100.0
        load = state.get("load", 1.0) if state else 1.0

        if node not in topology:
            topology.add_node(node, latency=latency, load=load)
        else:
            topology.nodes[node]["latency"] = latency
            topology.nodes[node]["load"] = load

    for change in changes:
        node = change["node"]
        neighbors = change.get("neighbors", [])

        ipv4, port = node.split(":")
        add_or_update_node(node, ipv4, port)

        for neighbor in neighbors:
            neighbor_ipv4, neighbor_port = neighbor.split(":")
            add_or_update_node(neighbor, neighbor_ipv4, neighbor_port)

            # Fetch latency and load for weight calculation
            node_latency = topology.nodes[node].get("latency", 100.0)
            neighbor_latency = topology.nodes[neighbor].get("latency", 100.0)
            node_load = topology.nodes[node].get("load", 1.0)
            neighbor_load = topology.nodes[neighbor].get("load", 1.0)

            # Calculate weight and update edge
            weight = calculate_weight(node_latency, neighbor_latency, node_load, neighbor_load)
            topology.add_edge(node, neighbor, weight=weight)

    return topology




















