# comprehensive_simulation.py - Written by Yuchen
"""
    This script simulates the dynamic addition and removal of satellites in a network.
"""

import subprocess
import time
import json
import os
import random
import logging
import argparse
from typing import List, Dict
import networkx as nx
import platform

# Configure logging
logging.basicConfig(
    filename="simulation.log",  # Path to the log file
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Path to the configuration file
CONFIG_FILE = "satellites_config.json"
MOCK_SCRIPT = "mock_satellite.py"

def get_ip_address() -> List[str]:
    """
    Get the IP address of the current machine.
    Supported OS: macOS, Linux, Windows.
    """
    available_ips = [os.getenv("IP")]

    if available_ips[0] is None:
        current_os = platform.system()
        try:
            if current_os == "Darwin":  # macOS
                try:
                    result = subprocess.check_output(["ipconfig", "getifaddr", "en0"], stderr=subprocess.STDOUT)
                    ip_en0 = result.decode("utf-8").strip()
                    if ip_en0:
                        available_ips.append(ip_en0)
                except subprocess.CalledProcessError:
                    logging.warning("无法获取 en0 接口的 IP 地址。")

                try:
                    result = subprocess.check_output(["ipconfig", "getifaddr", "en1"], stderr=subprocess.STDOUT)
                    ip_en1 = result.decode("utf-8").strip()
                    if ip_en1:
                        available_ips.append(ip_en1)
                except subprocess.CalledProcessError:
                    logging.warning("Cannot get IP address of en1 interface.")

            elif current_os == "Linux":
                result = subprocess.check_output(["hostname", "-I"], stderr=subprocess.STDOUT)
                ips = result.decode("utf-8").strip().split()
                available_ips.extend(ips)

            elif current_os == "Windows":
                result = subprocess.check_output(["ipconfig"], stderr=subprocess.STDOUT, text=True, encoding='utf-8')
                ips = []
                for line in result.splitlines():
                    line = line.strip()
                    if line.startswith("IPv4 Address") or line.startswith("IPv4-adresse"):  # 处理英文和德文
                        ip = line.split(":")[-1].strip()
                        ips.append(ip)
                available_ips.extend(ips)

            else:
                logging.error(f"Unsupported OS: {current_os}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get IP address: {e.output.decode('utf-8')}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while getting IP address: {str(e)}")

        available_ips = list(filter(None, available_ips))
        available_ips = list(dict.fromkeys(available_ips))

    logging.info(f"Available IPs: {available_ips}")
    return available_ips

# Define available IP addresses
AVAILABLE_IPS = [os.getenv("IP")]
if AVAILABLE_IPS[0] is None:
    AVAILABLE_IPS = get_ip_address()

processes = []  # List to keep track of running mock satellites

def load_config(config_file: str) -> Dict:
    """Load the configuration from a file."""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        logging.info("Configuration file loaded.")
        return config
    else:
        logging.warning("Configuration file not found, generating a new one.")
        return {"satellites": []}

def save_config(config_file: str, config: Dict):
    """Save the configuration to a file."""
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    logging.info(f"Configuration file saved: {config_file}")

def generate_random_port(existing_ports: set, min_port: int = 33001, max_port: int = 33100) -> int:
    """Generate a random port number that is not in the existing ports."""
    while True:
        port = random.randint(min_port, max_port)
        if port not in existing_ports:
            return port

def start_mock_satellite(ip: str, port: int) -> subprocess.Popen:
    """Start a Mock Satellite process."""
    try:
        process = subprocess.Popen(
            ['python', MOCK_SCRIPT, '--ip', ip, '--port', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logging.info(f"Mock Satellite started: {ip}:{port}")
        return process
    except Exception as e:
        logging.error(f"Failed to start Mock Satellite: {ip}:{port}, error: {e}")
        return None

def stop_mock_satellite(process: subprocess.Popen, ip: str, port: int):
    """Stop a Mock Satellite process."""
    try:
        process.terminate()
        process.wait(timeout=5)
        logging.info(f"Mock Satellite stopped: {ip}:{port}")
    except Exception as e:
        logging.error(f"Failed to stop Mock Satellite: {ip}:{port}, error: {e}")

def get_existing_ips(satellites: List[Dict]) -> set:
    """Get existing IP addresses."""
    return {sat['ip'] for sat in satellites}

def get_available_ips(satellites: List[Dict]) -> List[str]:
    """Return all available IP addresses without restricting the number of uses per IP."""
    return AVAILABLE_IPS.copy()

def assign_neighbors(satellites: List[Dict]):
    """
    Clean up non-existent neighbors and distribute new neighbors.
    """
    num_satellites = len(satellites)
    G = nx.Graph()

    # Add nodes to the graph
    for sat in satellites:
        node = f"{sat['ip']}:{sat['port']}"
        G.add_node(node)

    # Clean up non-existent neighbors
    for sat in satellites:
        current_neighbors = sat.get("neighbors", [])
        valid_neighbors = [
            neighbor for neighbor in current_neighbors
            if any(neighbor == f"{s['ip']}:{s['port']}" for s in satellites)
        ]
        sat["neighbors"] = valid_neighbors

    # Distribute new neighbors
    if num_satellites > 1:
        for sat in satellites:
            node = f"{sat['ip']}:{sat['port']}"
            possible_neighbors = [f"{s['ip']}:{s['port']}" for s in satellites if f"{s['ip']}:{s['port']}" != node]
            num_neighbors = random.randint(0, min(len(possible_neighbors), num_satellites - 1))
            neighbors = random.sample(possible_neighbors, num_neighbors)
            for neighbor in neighbors:
                if not G.has_edge(node, neighbor):
                    G.add_edge(node, neighbor)

    # Update neighbor list in the config
    for sat in satellites:
        node = f"{sat['ip']}:{sat['port']}"
        sat["neighbors"] = list(G.neighbors(node))
        logging.info(f"Neighbors of satellite {node}: {sat['neighbors']}")

def main():
    global processes

    parser = argparse.ArgumentParser(description="Satellite Simulation")
    parser.add_argument('--max_satellites', type=int, default=5, help="Maximum number of satellites to simulate")
    args = parser.parse_args()
    max_satellites = args.max_satellites

    while True:
        config = load_config(CONFIG_FILE)
        satellites = config.get("satellites", [])
        existing_ports = {sat['port'] for sat in satellites}

        # Calculate the number of satellites
        num_satellites = len(satellites)

        # Determine the action type
        if num_satellites == 0:
            action = 'add'
        elif num_satellites > max_satellites:
            action = 'remove'
        else:
            # 80% 'add' and 20% 'remove'
            action = random.choices(['add', 'remove'], weights=[80, 20], k=1)[0]

        if action == 'add':
            # Get available IPs
            available_ips = get_available_ips(satellites)
            if not available_ips:
                print("No available IPs to add new satellites.")
                logging.warning("Cannot add new satellites due to lack of available IPs.")
            else:
                # Select a random available IP
                ip = random.choice(available_ips)
                # Generate a unique port
                new_port = generate_random_port(existing_ports)
                new_satellite = {
                    "ip": ip,
                    "port": new_port,
                    "neighbors": []
                }
                satellites.append(new_satellite)
                logging.info(f"Added new satellite: {ip}:{new_port}")
                # Start the new Mock Satellite server
                process = start_mock_satellite(ip, new_port)
                if process:
                    processes.append((process, ip, new_port))
                # Assign neighbors
                assign_neighbors(satellites)
                # Update the configuration file
                config["satellites"] = satellites
                save_config(CONFIG_FILE, config)
        elif action == 'remove' and satellites:
            # Randomly remove a satellite
            removed_satellite = random.choice(satellites)
            satellites.remove(removed_satellite)
            logging.info(f"Removed satellite: {removed_satellite['ip']}:{removed_satellite['port']}")
            # Stop the corresponding Mock Satellite server
            for proc, ip, port in processes:
                if ip == removed_satellite['ip'] and port == removed_satellite['port']:
                    stop_mock_satellite(proc, ip, port)
                    processes.remove((proc, ip, port))
                    break
            # Remove all references to the removed satellite in the neighbors list
            removed_identity = f"{removed_satellite['ip']}:{removed_satellite['port']}"
            for satellite in satellites:
                if removed_identity in satellite.get("neighbors", []):
                    satellite["neighbors"].remove(removed_identity)

            # Update the configuration file
            config["satellites"] = satellites
            save_config(CONFIG_FILE, config)
        else:
            print("No satellites to remove.")
            logging.info("No satellites to remove.")

        # Wait for a random duration before the next operation
        sleep_duration = random.randint(10, 30)
        logging.info(f"Waiting {sleep_duration} seconds before the next operation.")
        time.sleep(sleep_duration)

if __name__ == "__main__":
    main()




