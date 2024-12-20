# Written by Claire, whale data generation written by Patrick
import threading
import random
import time
import argparse
import sys
import socket
import requests
import signal
import math
from src.utils.headers import necessary_headers
from src.discovery.discovery import find_x_satellites
from src.config.constants import BASESTATION

# TODO set up local verification
import urllib3
urllib3.disable_warnings()

proxies = {
    "http": "",
    "https": "",
}

def handle_sigint(signal, frame):
    print("Program interrupted. Exiting...")
    sys.exit(0)  # Exit the program

class WhaleModel:
    def __init__(self, whale_id, min_diving_time, max_diving_time, min_surface_time, max_surface_time, destination_ip, destination_port, satellite_ip, satellite_port, ip, port):
        self.whale_id = whale_id
        self.min_diving_time = min_diving_time
        self.max_diving_time = max_diving_time
        self.min_surface_time = min_surface_time
        self.max_surface_time = max_surface_time
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.satellite_ip = satellite_ip
        self.satellite_port = satellite_port
        self.ip = ip
        self.port = port

    def generate_whale_data(self, time_since_surfaced):
        whale_data_points = []
        
        # create sample data points for every 60 seconds since the time_since_surfaced
        for i in range(math.ceil(time_since_surfaced / 60)):
            whale_data_point = {
                "whale_id": self.whale_id,
                "timestamp": int(time.time()),
                "latitude": random.uniform(-90, 90),
                "longitude": random.uniform(-180, 180),
                "speed": random.uniform(0, 10),  # speed in m/s
                "depth": random.randint(0, 3000),  # depth in meters
                "water_temperature": random.uniform(-2, 30),  # in degrees Celsius
                "heart_rate": random.randint(30, 60),  # in beats per minute
                "energy_level": random.uniform(0, 100),  # arbitrary units
                "number_of_breaths": random.randint(1, 5),
                "heading": random.uniform(0, 360),  # degrees
            }
            whale_data_points.append(whale_data_point)
        
        return whale_data_points

    # Method to send data to the satellite when the whale resurfaces
    def send_data(self, time_since_surfaced):
        # Random time the whale will spend at the surface
        surface_time = random.randint(self.min_surface_time, self.max_surface_time)
        
        # Whale data collected since last surfaced
        sample_data = self.generate_whale_data(time_since_surfaced)
        print(time_since_surfaced)
        print(sample_data)

        # Prepare header
        header = necessary_headers.BobbHeaders(
            version_major=0,
            version_minor=0,
            message_type=0,
            dest_ipv4=self.destination_ip,
            dest_port=self.destination_port,
            source_ipv4=self.ip,
            source_port=self.port
        )
        header = header.build_header().hex()
        headers = {
            "X-Bobb-Header": header,
        }

        # Send acknowledgment request to satellite
        try:
            # TODO: enable verification
            response = requests.post(f"https://{self.satellite_ip}:{self.satellite_port}/call_satellite_from_whale", verify=False, timeout=surface_time, proxies=proxies, headers=headers, json= {
                "source": f"{self.ip}:{self.port}",
                "destination": f"{self.destination_ip}:{self.destination_port}",
                "message": sample_data,
                "priority": "high"
            })
            #response = requests.get(f"https://{self.satellite_ip}:{self.satellite_port}/route", headers=headers, verify=False, timeout=surface_time, proxies=proxies)
            print(f"Whale {self.whale_id} received response code {response.status_code} and content: {response.text}")
        except Exception as e:
            print(f"Failed to send data for whale {self.whale_id}: {e}")

    # Simulate whale routine with diving and resurfacing
    def start_whale_routine(self):
        while True:
            diving_time = random.randint(self.min_diving_time, self.max_diving_time)
            time.sleep(diving_time)  # Simulate whale diving

            # Whale surfaces
            time_since_surfaced = diving_time
            self.send_data(time_since_surfaced)

def main(num_whales, min_diving_time, max_diving_time, min_surface_time, max_surface_time, destination_ip, destination_port):
    # Set up the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, handle_sigint)

    whales = []
    base_port = 33700

    hostname = socket.gethostname()
    ip = socket.getaddrinfo(hostname, None, socket.AF_INET)[0][4][0]
    satellites = find_x_satellites(x=100)
    filtered_satellites = [entry for entry in satellites if entry["Device Function"] != BASESTATION]

    for whale_id in range(num_whales):
        # Assign a unique port to each whale
        port = base_port + whale_id

        satellite = random.choice(filtered_satellites)
        sat_ip = satellite["IPv4"]
        sat_port = satellite["Port"]
        whale = WhaleModel(whale_id, min_diving_time, max_diving_time, min_surface_time, max_surface_time, destination_ip, destination_port, sat_ip, sat_port, ip, port)
        
        # Start the whale routine in a separate thread
        threading.Thread(target=whale.start_whale_routine, daemon=True).start()
        
        whales.append(whale)

    print(f"{num_whales} whales modeled, each sending data to satellite at {destination_ip}:{destination_port}.")
    
    signal.pause()  # Wait indefinitely until a signal is received

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Model whales coming to the surface and diving deep, sending data when they are at the surface.")
    parser.add_argument("--num_whales", type=int, default=10, help="Number of whales to model (default: 10)")
    parser.add_argument("--min_diving_time", type=int, default=300, help="Minimum time a whale spends diving (in seconds, default: 300)")
    parser.add_argument("--max_diving_time", type=int, default=3600, help="Maximum time a whale spends diving (in seconds, default: 3600)")
    parser.add_argument("--min_surface_time", type=int, default=30, help="Minimum time a whale spends at the surface (in seconds, default: 30)")
    parser.add_argument("--max_surface_time", type=int, default=1200, help="Maximum time a whale spends at the surface (in seconds, default: 1200)")
    parser.add_argument("--destination_ip", type=str, help="Destination base station ip address")
    parser.add_argument("--destination_port", type=int, help="Destination base station port")
    args = parser.parse_args()

    # Start the model
    main(args.num_whales, args.min_diving_time, args.max_diving_time, args.min_surface_time, args.max_surface_time, args.destination_ip, args.destination_port)
