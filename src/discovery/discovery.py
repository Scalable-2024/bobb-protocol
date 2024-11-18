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

from src.helpers.send_handshake_helper import send_handshakes

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
    
def find_x_satellites(ips_to_check=None, min_port=33001, max_port=33100, endpoint="id", x=5, port=None):
    results = []

    print(ips_to_check)

    ip = os.getenv("IP")
    # If on a private IP address, assume raspberry pis
    if ip.split('.')[0] == "10":
        # Default list of ips to check - raspberry pi IPs
        if ips_to_check is None:
            ips_to_check = ["10.35.70."+str(extension) for extension in range(1, 50)]
    else:
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
    port = os.getenv("PORT")
    starter_satellite_list = find_x_satellites(x=5, port=int(port))

    base_dir = os.getcwd()
    directory_path = os.path.join(base_dir, "resources", "satellite_listings")
    file_name = os.path.join(directory_path, f"full_satellite_listing_{port}.csv")
    os.makedirs(directory_path, exist_ok=True)

    with open(file_name, "w", newline="") as csvfile:
        print(f"Writing to {file_name}")
        fieldnames = ["IPv4", "Port", "Contact Time", "Device Function"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(starter_satellite_list)

    send_handshakes()