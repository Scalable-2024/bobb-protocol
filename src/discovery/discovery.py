import argparse
import subprocess
import re
import csv
import requests
import os
import random
import re
from src.config.config import valid_functions

# TODO allow self signed certificates
import urllib3
urllib3.disable_warnings()

# To block the SCSS proxying, to connect directly to the other pis
proxies = {
  'http': '',
  'https': '',
}


def ping_with_response_time(ipv4, timeout=1):
    """Ping an IPv4 address and return the response time in ms."""
    try:
        output = subprocess.check_output(
            "ping -c 1 -W {} {}".format(timeout, ipv4),
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL
        )
        match = re.search(r'time=(\d+\.\d+) ms', output)
        if match:
            return float(match.group(1))
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
            data = resp.json()['data']
            print(f"Data: {data}")
            if data in valid_functions:
                return data
            
        return None
    except Exception as e:
        if verbose:
            print(f"Got error: {e}")
        return None
    
def find_x_satellites(ips_to_check=["172.31.116.126"], min_port=33001, max_port=33100, endpoint="id", x=5):
    results = []

    # Default list of ips to check - raspberry pi IPs
    if ips_to_check is None:
        ips_to_check = ["10.35.70."+str(extension) for extension in range(1, 50)]

    for ip in ips_to_check:
        response_time = ping_with_response_time(ip)
        if response_time is not None:
            for port in range(min_port, max_port+1):
                function = check_device_type(ip, port, endpoint, verbose=False)
                # The only case we care about is when the IP and port are valid
                if function is not None:
                    results.append({
                        "IPv4": ip,
                        "Port": port,
                        "Response Time": response_time,
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
    starter_satellite_list = find_x_satellites(x=5)

    port = os.getenv("PORT")
    base_dir = os.getcwd()
    directory_path = os.path.join(base_dir, "resources", "satellite_listings")
    file_name = os.path.join(directory_path, f"full_satellite_listing_{port}.csv")
    os.makedirs(directory_path, exist_ok=True)

    with open(file_name, "w", newline="") as csvfile:
        fieldnames = ["IPv4", "Port", "Response Time", "Device Function"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(starter_satellite_list)



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
