import argparse
import subprocess
import re
import csv
import requests

# TODO allow self signed certificates
import urllib3
urllib3.disable_warnings()

# To block the SCSS proxying, to connect directly to the other pis
proxies = {
  'http': '',
  'https': '',
}


def ipv4_to_ipv6(ipv4):
    """Convert an IPv4 address to IPv6 using the ::ffff: method."""
    return "::ffff:{}".format(ipv4)


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


def check_if_satellite(ipv4, port, endpoint):
    """Make an HTTP request using curl and return the response message if status code is 200."""
    try:
        # Log to indicate progress
        addr = f"https://{ipv4}:{port}/{endpoint}"
        print(f"Attempting HTTP request to {addr}...")
        # TODO: Allow self signed certificates
        resp = requests.get(addr, verify=False, timeout=3, proxies=proxies)
        # Check the HTTP status code and response
        if resp.status_code == 200:
            print(f"HTTP 200 OK from {addr}")
            json = resp.json()
            if json["data"] == "I am a satellite":
                return True
            else:
                print(f"{addr} is responding, but is not verified to be a bobb satellite - {json['data']} does not equal 'I am a satellite'")
        return False
    except Exception as e:
        print(f"Got error: {e}")
        return False


def main(ping_ip, port, output_csv, endpoint):
    results = []
    for ip in range(1, 50):  # Example scan of 50 IPs, adjust range as needed
        ipv4 = "{}.{}".format(ping_ip, ip)
        print(f"Pinging {ipv4}...")
        response_time = ping_with_response_time(ipv4)
        if response_time is not None:
            print(f"{ipv4} is active. Fetching HTTP response...")
            ipv6 = ipv4_to_ipv6(ipv4)
            is_satellite = check_if_satellite(ipv4, port, endpoint)
            results.append({
                "IPv4": ipv4,
                "IPv6": ipv6,
                "Response Time (ms)": response_time,
                "Is a satellite?": is_satellite
            })
        else:
            print(f"{ipv4} did not respond. Skipping HTTP request.")
    # Sort results by response time
    sorted_results = sorted(results, key=lambda x: x["Response Time (ms)"])
    # Write results to CSV
    with open(output_csv, "w", newline="") as csvfile:
        fieldnames = ["IPv4", "IPv6", "Response Time (ms)", "Is a satellite?"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_results)
    print(f"CSV file '{output_csv}' has been created.")


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