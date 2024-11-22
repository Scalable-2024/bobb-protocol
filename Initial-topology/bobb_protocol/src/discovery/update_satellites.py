# bobb_protocol/src/discovery/update_satellites.py
import os
import pickle
import time
import json
import csv
from datetime import datetime
from discovery import discover_satellites, build_topology, update_topology, visualize_topology
from satellite_utils import remove_offline_satellites, update_satellite_status

# Writen by Yuchen
"""
    This script simulates dynamic updates to the network topology based on satellite status and configuration changes.
"""
def save_topology(topology, topology_file):
    """Save the network topology to a file."""
    with open(topology_file, "wb") as f:
        pickle.dump(topology, f)
    print(f"Topology saved to {topology_file}.")

def load_topology(topology_file):
    """Load the network topology from a file."""
    with open(topology_file, "rb") as f:
        return pickle.load(f)

def detect_new_satellites(config, current_topology):
    """Detect new satellites that are not yet in the current topology."""
    existing_nodes = set(current_topology.nodes())
    new_satellites = []

    for satellite in config['satellites']:
        ip = satellite['ip']
        port = satellite['port']
        node = f"{ip}:{port}"

        if node not in existing_nodes:
            print(f"New satellite detected: {node}")
            new_satellites.append(node)
            current_topology.add_node(node, latency=None, load=None)  # 添加到拓扑

    return list(set(new_satellites))  # Avoid duplicates

def write_to_csv(satellites, csv_file):
    """Write satellite information to a CSV file."""
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    with open(csv_file, mode="w", newline="") as csvfile:
        fieldnames = ["IPv4", "IPv6", "Response Time (ms)", "Is a Satellite?", "Neighbors"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for satellite in satellites:
            writer.writerow({
                "IPv4": satellite["ipv4"],
                "IPv6": satellite["ipv6"],
                "Response Time (ms)": satellite["response time (ms)"],
                "Is a Satellite?": satellite["is a satellite?"],
                "Neighbors": satellite["neighbors"] if satellite["neighbors"] else []
            })

def simulate_dynamic_updates(config_file, topology_file, csv_file, update_interval=10, log_file="topology_log.txt"):
    """Simulate dynamic updates and maintain the network topology."""
    if not os.path.exists(topology_file) or os.path.getsize(topology_file) == 0:
        print("Topology file does not exist or is empty. Creating a new topology.")
        satellites = discover_satellites(config_file, "/id", "/neighbors")
        topology = build_topology(satellites)
        save_topology(topology, topology_file)
    else:
        print(f"Loading existing topology from {topology_file}.")
        topology = load_topology(topology_file)

    while True:
        with open(config_file, 'r') as f:
            config = json.load(f)

        # Update satellite status (latency, load)
        topology = update_satellite_status(topology, config)

        # Remove offline satellites
        topology = remove_offline_satellites(topology, config)

        # Detect and add new satellites
        new_satellites = detect_new_satellites(config, topology)
        for node in new_satellites:
            topology.add_node(node, latency=None, load=None)

        # Update the topology based on new neighbors
        changes = []
        for satellite in config['satellites']:
            ip = satellite['ip']
            port = satellite['port']
            node = f"{ip}:{port}"
            neighbors = satellite.get("neighbors", [])
            changes.append({"node": node, "neighbors": neighbors})

        topology = update_topology(topology, changes)

        # Save the updated topology
        save_topology(topology, topology_file)

        # Log the current topology state
        log_topology_state(topology, log_file)

        # Visualize the updated topology
        visualize_topology(topology, interval=5)

        print("Updated topology logged to file.")

        # Prepare satellite information for CSV export
        satellites = discover_satellites(config_file)
        satellites_info = []
        for ip, info in satellites.items():
            ipv4 = ip.split(":")[0]
            neighbors = info.get("neighbors", [])
            satellite = {
                "ipv4": ipv4,
                "ipv6": info.get("ipv6", "::ffff:" + ipv4),
                "response time (ms)": info.get("response time (ms)", "N/A"),
                "is a satellite?": info.get("is a satellite?", False),
                "neighbors": neighbors if neighbors else []
            }
            satellites_info.append(satellite)

        # Write the satellite information to the CSV file
        write_to_csv(satellites_info, csv_file)

        print(f"Satellite information saved to {csv_file}.")

        # Wait before the next update
        time.sleep(update_interval)

def log_topology_state(topology, log_file="topology_log.txt"):
    """Log the current topology state to a file with a timestamp."""
    with open(log_file, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n--- Topology state at {timestamp} ---\n")
        for edge in topology.edges(data=True):
            f.write(f"{edge}\n")
        f.write("\n")  # Add a new line for separation

if __name__ == "__main__":
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    config_file = os.path.join(root_path, "satellites_config.json")
    topology_file = os.path.join(root_path, "topology.pkl")
    result_csv_file = os.path.join(root_path, "result.csv")

    simulate_dynamic_updates(config_file, topology_file, result_csv_file, update_interval=10)

    #  export PYTHONPATH=$(pwd)






