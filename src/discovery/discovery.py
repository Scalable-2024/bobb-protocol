import argparse
import logging
import subprocess
import re
import csv
import requests
import os
import random
import re
import time
from src.config.config import valid_functions

# TODO allow self signed certificates
import urllib3
urllib3.disable_warnings()

# To block the SCSS proxying, to connect directly to the other pis
proxies = {
  'http': '',
  'https': '',
}


def ping_with_contact_time(ipv4, timeout=1):
    """Ping an IPv4 address and return the last contact time as a UNIX timestamp"""
    try:
        output = subprocess.check_output(
            "ping -c 1 -W {} {}".format(timeout, ipv4),
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL
        )
        match = re.search(r'time=(\d+\.\d+) ms', output)
        if match:
            return int(time.time())  # Return the current time as a UNIX timestamp
        return None
    except subprocess.CalledProcessError:
        return None  # Ping failed or timeout


def check_device_type(ipv4, port, endpoint, verbose):
    """Make an HTTP request using curl and return the response message if status code is 200."""
    try:
        # Log to indicate progress
        addr = f"https://{ipv4}:{port}/{endpoint}"
        if verbose:
            print(f"Attempting HTTP request to {addr}...")
        # TODO: Allow self signed certificates
        resp = requests.get(addr, verify=False, timeout=3, proxies=proxies)
        # Check the HTTP status code and response
        if resp.status_code == 200:
            if verbose:
                print(f"HTTP 200 OK from {addr}")
            function = resp.json()['data']
            if function in valid_functions:
                return function
            
        return None
    except Exception as e:
        if verbose:
            print(f"Got error: {e}")
        return None
    
def find_x_satellites(ips_to_check=None, min_port=33001, max_port=33030, endpoint="id", x=10, port=None): #33100 to
    results = []

    print(ips_to_check)

    # Default list of ips to check - raspberry pi IPs
    if ips_to_check is None:
        # ips_to_check = ["10.35.70."+str(extension) for extension in range(1, 50)]
        ips_to_check = ["localhost"] # <- for local testing

    for ip in ips_to_check:
        contact_time = ping_with_contact_time(ip)
        print(f"Time of last contact for {ip}: {contact_time}")
        if contact_time is not None:
            for queried_port in range(min_port, max_port + 1):
                if queried_port == port:
                    print(f"Skipping port {queried_port} as that is our own port.")
                    continue
                function = check_device_type(ip, queried_port, endpoint, verbose=False)
                # The only case we care about is when the IP and port are valid
                if function is not None:
                    print(f"Found {ip}:{queried_port} with function {function}")
                    results.append({
                        "IPv4": ip,
                        "Port": queried_port,
                        "Contact Time": contact_time,
                        "Device Function": function,
                    })
    
    # Randomly select x satellites from the results
    if len(results) > x:
        selected_results = random.sample(results, x)
    else:
        # If there are fewer than x results, return all of them
        selected_results = results

    return selected_results

# Note that this is finding the list of potential satellites, outside of the simulation.
# This is because we need the ip addresses to simulate communication.
# It should return the intended neighbour satellites - for now, just the ones with the lowest latency.
def get_neighbouring_satellites():
    # Get the port number from the environment variable
    port = os.getenv("PORT")
    if not port:
        raise ValueError("PORT environment variable is not set.")
    print(f"[DEBUG] PORT environment variable is set to: {port}")

    # Find a list of 20 potential satellites using the specified port
    print("[DEBUG] Starting satellite discovery...")
    starter_satellite_list = find_x_satellites(x=10, port=int(port))
    print(f"[DEBUG] Discovered {len(starter_satellite_list)} satellites.")

    # Define the base directory for resources
    base_dir = os.getcwd()
    print(f"[DEBUG] Base directory: {base_dir}")

    # Define paths for satellite listings and to-be-discovered directories
    directory_path = os.path.join(base_dir, "resources", "satellite_listings")
    discovery_dir = os.path.join(base_dir, "resources", "to_be_discovered")
    print(f"[DEBUG] Satellite listings directory path: {directory_path}")
    print(f"[DEBUG] To-be-discovered directory path: {discovery_dir}")

    # Define file paths for the full satellite listing and to-be-discovered files
    file_name = os.path.join(directory_path, f"full_satellite_listing_{port}.csv")
    discovery_file = os.path.join(discovery_dir, f"to_be_discovered_{port}.csv")
    print(f"[DEBUG] Full satellite listing file path: {file_name}")
    print(f"[DEBUG] To-be-discovered file path: {discovery_file}")

    # Ensure the directories exist
    print("[DEBUG] Ensuring directories exist...")
    os.makedirs(directory_path, exist_ok=True)
    os.makedirs(discovery_dir, exist_ok=True)

    # Calculate the number of satellites to move to the to-be-discovered list (5% of the total)
    total_satellites = len(starter_satellite_list)
    discovery_count = max(1, int(total_satellites * 0.05))  # Ensure at least 1 satellite is selected
    print(f"[DEBUG] Total satellites: {total_satellites}, Discovery count (5%): {discovery_count}")

    # Split the starter list into to-be-discovered and remaining satellites
    to_be_discovered = starter_satellite_list[:discovery_count]  # First 5% for discovery
    remaining_satellites = starter_satellite_list[discovery_count:]  # Remaining 95%
    print(f"[DEBUG] To-be-discovered satellites: {len(to_be_discovered)}")
    print(f"[DEBUG] Remaining satellites: {len(remaining_satellites)}")

    # Write the remaining satellites to the full satellite listing file
    try:
        with open(file_name, "w", newline="") as csvfile:
            print(f"[DEBUG] Writing full satellite listing to {file_name}")
            fieldnames = ["IPv4", "Port", "Contact Time", "Device Function"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(remaining_satellites)  # Write the remaining satellites to the file
    except Exception as e:
        print(f"[ERROR] Failed to write full satellite listing: {e}")

    # Write the to-be-discovered satellites to the discovery file
    try:
        with open(discovery_file, "w", newline="") as csvfile:
            print(f"[DEBUG] Writing to_be_discovered list to {discovery_file}")
            fieldnames = ["IPv4", "Port", "Contact Time", "Device Function"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(to_be_discovered)  # Write the to-be-discovered satellites to the file
    except Exception as e:
        print(f"[ERROR] Failed to write to_be_discovered list: {e}")


    # with open(file_name, "w", newline="") as csvfile:
    #     print(f"Writing to {file_name}")
    #     fieldnames = ["IPv4", "Port", "Contact Time", "Device Function"]
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()
    #     writer.writerows(starter_satellite_list)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ping sweep for a given network and save results to CSV.")
    parser.add_argument("--ping_ip", default="10.35.70",
                        help="Base IP address for ping (e.g., 192.168.1)")
    parser.add_argument("--port", default=33001,
                        help="Port which will serve satellite identification")
    parser.add_argument("--output_csv", default="results.csv",
                        help="Output CSV file name (e.g., results.csv)")
    parser.add_argument('--endpoint', default="id",
                        help="The endpoint which the satellite serves its identification on - eg /id")
    args = parser.parse_args()
    main(args.ping_ip, args.port, args.output_csv, args.endpoint)

