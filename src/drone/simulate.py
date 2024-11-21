# Written by OuYang, Modified by Eoghan
import threading
import random
import time
import argparse
import sys
import socket
import requests
import signal
import math
from flask import Flask, jsonify

from src.utils.headers.necessary_headers import BobbHeaders
from src.utils.headers.optional_header import BobbOptionalHeaders
from src.discovery.discovery import find_x_satellites
from src.config.constants import BASESTATION

# Disable SSL warnings (optional)
import urllib3
urllib3.disable_warnings()

proxies = {
    "http": "",
    "https": "",
}

def handle_sigint(signal, frame):
    print("Program interrupted. Exiting...")
    sys.exit(0)  # Exit the program

class DroneModel:
    def __init__(self, drone_id, destination_ip, destination_port, satellite_ip, satellite_port, ip, port):
        self.drone_id = drone_id
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.satellite_ip = satellite_ip
        self.satellite_port = satellite_port
        self.ip = ip
        self.port = port

    def generate_drone_data(self):
        """
        Simulate and generate data to send, including environmental and survivor data.
        """
        latitude = random.uniform(-90, 90)
        longitude = random.uniform(-180, 180)
        water_level = random.uniform(0.5, 5.0)
        temperature = random.uniform(15, 40)
        humidity = random.randint(50, 100)
        air_quality_index = random.randint(50, 300)

        num_survivors = random.randint(0, 5)
        survivors = []
        for _ in range(num_survivors):
            survivor_id = random.randint(10000, 99999)
            survivor_location = {
                "latitude": random.uniform(latitude - 0.01, latitude + 0.01),
                "longitude": random.uniform(longitude - 0.01, longitude + 0.01)
            }
            survivor_status = random.choice(["injured", "uninjured"])
            survivor_survival_time = random.randint(600, 1800)  # Survival time in seconds
            survivors.append({
                "survivor_id": survivor_id,
                "location": survivor_location,
                "status": survivor_status,
                "survival_time": survivor_survival_time
            })

        drone_data = {
            "drone_id": self.drone_id,
            "timestamp": int(time.time()),
            "data": {
                "survivors": survivors,
                "environment": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "water_level": water_level,
                    "temperature": temperature,
                    "humidity": humidity,
                    "air_quality_index": air_quality_index
                }
            }
        }

        return drone_data

    def send_data(self):
        """
        Simulate data transmission to the satellite.
        """
        # Generate drone data
        drone_data = self.generate_drone_data()

        # Prepare headers
        header = BobbHeaders(
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

        try:
            # Send data to satellite
            response = requests.post(
                f"https://{self.satellite_ip}:{self.satellite_port}/call_satellite_from_drone",
                verify=False,
                timeout=10,
                proxies=proxies,
                headers=headers,
                json={
                    "source": f"{self.ip}:{self.port}",
                    "destination": f"{self.destination_ip}:{self.destination_port}",
                    "message": drone_data,
                    "priority": "high"
                }
            )
            print(f"Drone {self.drone_id} sent data, received response: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Drone {self.drone_id} failed to send data: {e}")

    def start_drone_routine(self):
        """
        Simulate the drone's data collection and sending routine.
        """
        while True:
            # Random delay between 40 seconds and 5 minutes
            interval = random.randint(10, 60)
            time.sleep(interval)

            # Send the data
            self.send_data()

def main(num_drones, destination_ip, destination_port):
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, handle_sigint)

    drones = []
    base_port = 40000

    hostname = socket.gethostname()
    ip = socket.getaddrinfo(hostname, None, socket.AF_INET)[0][4][0]
    satellites = find_x_satellites(x=100)
    filtered_satellites = [entry for entry in satellites if entry["Device Function"] != BASESTATION]

    for drone_id in range(num_drones):
        # Assign a unique port to each drone
        port = base_port + drone_id

        # Randomly select a satellite for communication
        satellite = random.choice(filtered_satellites)
        sat_ip = satellite["IPv4"]
        sat_port = satellite["Port"]

        # Create and start a drone model
        drone = DroneModel(drone_id, destination_ip, destination_port, sat_ip, sat_port, ip, port)
        threading.Thread(target=drone.start_drone_routine, daemon=True).start()
        drones.append(drone)

    print(f"{num_drones} drones modeled, each sending data to satellite at {destination_ip}:{destination_port}.")
    signal.pause()  # Wait indefinitely until a signal is received

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Simulate drones sending data to satellites.")
    parser.add_argument("--num_drones", type=int, default=5, help="Number of drones to simulate (default: 5)")
    parser.add_argument("--destination_ip", type=str, help="Destination base station IP address")
    parser.add_argument("--destination_port", type=int, help="Destination base station port")
    args = parser.parse_args()

    # Start the drone simulation
    main(args.num_drones, args.destination_ip, args.destination_port)
