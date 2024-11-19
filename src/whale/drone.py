# import requests
# from flask import Flask, request, jsonify, g
# import time
# from bobb.src.utils.crypto_utils.data_encryption import encrypt_data, decrypt_data, derive_shared_key
# from bobb.src.utils.crypto_utils.key_management import read_private_key, read_public_key
# from bobb.src.utils.headers.necessary_headers import BobbHeaders
# from bobb.src.utils.headers.optional_header import BobbOptionalHeaders
# import json
#
# app = Flask(__name__)
#

# drone_private_key = read_private_key("keys/drone_private_key.pem")
# satellite_public_key = read_public_key("keys/satellite_public_key.pem")
#
# # Generate a shared secret using the private key and the recipient's public key
# def get_shared_key(receiver_public_key):
#     return derive_shared_key(drone_private_key, receiver_public_key)
#
# @app.after_request
# def add_headers_and_encrypt(response):
#     """加密响应并添加协议头"""
#     try:
#         # 构造 Bobb 协议头部
#         bobb_response_header = BobbHeaders(
#             version_major=1,
#             version_minor=0,
#             message_type=2,
#             sequence_number=123,
#             timestamp=int(time.time())
#         )
#         response.headers["X-Bobb-Header"] = bobb_response_header.build_header().hex()
#
#         optional_response_header = BobbOptionalHeaders(
#             timestamp=int(time.time()),
#             hop_count=5,
#             priority=1,
#             encryption_algo="AES256"
#         )
#         response.headers["X-Bobb-Optional-Header"] = optional_response_header.build_optional_header().hex()
#
#         # 检查并加密响应数据
#         shared_key = get_shared_key(satellite_public_key)
#         if response.is_json:
#             encrypted_response = encrypt_data(json.dumps(response.get_json()).encode('utf-8'), shared_key)
#             response.headers["X-Bobb-Encrypted-Data"] = encrypted_response.hex()
#
#     except Exception as e:
#         return jsonify({"error": "Failed to encrypt response", "details": str(e)}), 500
#
#     return response
#
# @app.route("/handshake", methods=["POST"])
# def handshake():
#     """处理握手逻辑"""
#     return jsonify({
#         "status": "success",
#         "message": "Handshake received by Drone",
#         "data": request.json
#     })
#
# @app.route("/send_data", methods=["POST"])
# def send_data():
#     """发送加密数据到卫星"""
#     data_payload = {
#         "disaster": "flood",
#         "location": "Region A",
#         "survivors_detected": 23
#     }
#
#     try:
#         data_as_bytes = json.dumps(data_payload).encode('utf-8')
#
#         shared_key = get_shared_key(satellite_public_key)
#         encrypted_payload = encrypt_data(data_as_bytes, shared_key).hex()
#
#         headers = {
#             "X-Bobb-Encrypted-Data": encrypted_payload,
#             "Content-Type": "application/json",
#         }
#         satellite_url = "http://127.0.0.1:5002/relay_data"
#
#         # 发送到卫星
#         response = requests.post(satellite_url, json={}, headers=headers)
#
#         try:
#             satellite_response = response.json()
#         except ValueError:
#             satellite_response = {"error": "Invalid JSON response from satellite"}
#
#         return jsonify({
#             "status": "success",
#             "satellite_response": satellite_response
#         })
#
#     except Exception as e:
#         # 捕获异常并返回 JSON 响应
#         print(f"Error in /send_data: {str(e)}")
#         return jsonify({"error": "Failed to send data", "details": str(e)}),
#
# if __name__ == "__main__":
#     app.run(port=5001, debug=True)

import threading
import random
import time
import argparse
import os
import sys
import socket
import requests
import signal
from flask import Flask, jsonify

# TODO set up local verification
import urllib3
urllib3.disable_warnings()

from src.utils.headers.necessary_headers import BobbHeaders
from src.utils.headers.optional_header import BobbOptionalHeaders

proxies = {
    "http": "",
    "https": "",
}

def handle_sigint(signal, frame):
    print("Program interrupted. Exiting...")
    sys.exit(0)  # Exit the program

class DroneModel:
    def __init__(self, drone_id, task_type, destination_ip, destination_port, satellite_host, satellite_port, ip, port):
        self.drone_id = drone_id
        self.task_type = task_type  # Type of task (e.g., "flood-survivor-detection")
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.satellite_host = satellite_host
        self.satellite_port = satellite_port
        self.ip = ip
        self.port = port
        self.app = Flask(f"drone_{drone_id}")

        # Data for the drone, initialized with random values
        self.latitude = random.uniform(-90.0, 90.0)
        self.longitude = random.uniform(-180.0, 180.0)
        self.water_level = random.uniform(0.5, 5.0)
        self.temperature = random.uniform(15, 40)
        self.humidity = random.randint(50, 100)
        self.air_quality_index = random.randint(50, 300)

        # Define the Flask app to handle simple acknowledgment requests
        @self.app.route('/', methods=['GET'])
        def acknowledge():
            return jsonify({"message": "Acknowledged", "drone_id": self.drone_id})

    # Generate and update simulated data for sending, including random survivors
    def generate_sample_data(self):
        # Update the data to simulate real-time changes
        self.latitude += random.uniform(-0.001, 0.001)  # Simulate small movement
        self.longitude += random.uniform(-0.001, 0.001)  # Simulate small movement
        self.water_level += random.uniform(-0.05, 0.05)  # Simulate water level change
        self.temperature += random.uniform(-0.2, 0.2)  # Simulate temperature fluctuation
        self.humidity += random.randint(-5, 5)  # Simulate humidity fluctuation
        self.air_quality_index += random.randint(-5, 5)  # Simulate air quality fluctuation

        # Randomly generate 0 or more survivors
        num_survivors = random.randint(0, 5)  # Change the maximum number of survivors if needed
        survivors = []

        for _ in range(num_survivors):
            survivor_id = random.randint(10000, 99999)
            survivor_location = {
                "latitude": random.uniform(self.latitude - 0.01, self.latitude + 0.01),
                "longitude": random.uniform(self.longitude - 0.01, self.longitude + 0.01)
            }
            survivor_status = random.choice(["injured", "uninjured"])
            survivor_survival_time = random.randint(600, 1800)  # Survival time in seconds
            survivors.append({
                "survivor_id": survivor_id,
                "location": survivor_location,
                "status": survivor_status,
                "survival_time": survivor_survival_time
            })

        # Generate the new data dictionary to be sent
        data = {
            "drone_id": self.drone_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "data": {
                "survivors": survivors,  # Include the randomly generated survivors list
                "environment": {
                    "water_level": self.water_level,
                    "temperature": self.temperature,
                    "humidity": self.humidity,
                    "air_quality_index": self.air_quality_index
                }
            }
        }
        return data

    # Method to send data to the satellite when the drone collects data
    def send_data(self, data):
        # Prepare header for communication with the satellite or base station
        nece_headers = BobbHeaders(
            version_major=0,
            version_minor=0,
            message_type=0,
            dest_ipv4=self.destination_ip,
            dest_port=self.destination_port,
            source_ipv4=self.ip,
            source_port=self.port
        )
        try:
            nece_headers = nece_headers.build_header().hex()
        except ValueError as e:
            print(f"Drone {self.drone_id}: Error in building headers - {e}")
            return

        # Prepare optional header for communication with the satellite or base station
        opt_headers = BobbOptionalHeaders(
            timestamp=int(time.time()),
            hop_count=5,
            priority=1,
            encryption_algo="AES128"
        )
        opt_headers = opt_headers.build_optional_header().hex()

        headers = {
            "X-Bobb-Header": nece_headers,
            "X-Bobb-Optional-Header": opt_headers
        }

        # Send data to satellite (or base station)
        try:
            response = requests.get(f"https://{self.satellite_host}:{self.satellite_port}/", json=data, headers=headers, verify=False, proxies=proxies)
            print(f"Drone {self.drone_id} sent data: {data}, received response: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Drone {self.drone_id} failed to send data: {e}")

    # Simulate drone task with fixed interval (every 30 seconds)
    def start_drone_routine(self):
        while True:
            time.sleep(30)  # Wait for 30 seconds before performing the next task

            # Generate updated data and send
            data = self.generate_sample_data()
            self.send_data(data)

    # Start the Flask app for this drone in a separate thread
    def start_flask_app(self):
        threading.Thread(target=self.app.run, kwargs={"port": self.port, "use_reloader": False, "debug": False}, daemon=True).start()

# Main function and other parts remain the same

def main(num_drones, destination_ip, destination_port, satellite_host, satellite_port):
    # Set up the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, handle_sigint)

    drones = []
    base_port = 30000

    hostname = socket.gethostname()
    addresses = socket.getaddrinfo(hostname, None, socket.AF_INET)

    if addresses:
        ip = addresses[0][4][0]
    else:
        raise RuntimeError("No IPv4 address found for the host")

    for drone_id in range(num_drones):
        # Assign a unique port to each drone
        port = base_port + drone_id
        drone = DroneModel(drone_id, "flood-survivor-detection", destination_ip, destination_port, satellite_host,
                           satellite_port, ip, port)

        # Start the Flask app for each drone
        drone.start_flask_app()

        # Start the drone task in a separate thread
        threading.Thread(target=drone.start_drone_routine, daemon=True).start()

        drones.append(drone)

    print(f"{num_drones} drones modeled, each listening on individual ports starting from {base_port}.")

    signal.pause()  # Wait indefinitely until a signal is received

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Model drones for flood survivor detection with real-time data updates.")
    parser.add_argument("--num_drones", type=int, default=5, help="Number of drones to simulate (default: 5)")
    parser.add_argument("--destination_ip", type=str, help="Destination base station IP address")
    parser.add_argument("--destination_port", type=int, help="Destination base station port")
    parser.add_argument("--satellite_host", type=str, default="127.0.0.1", help="Satellite host")
    parser.add_argument("--satellite_port", type=int, default=8189, help="Satellite port")
    args = parser.parse_args()

    # Start the drone model
    main(args.num_drones, args.destination_ip, args.destination_port, args.satellite_host, args.satellite_port)
