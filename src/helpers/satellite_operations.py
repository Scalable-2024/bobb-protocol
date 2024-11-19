import os
import threading
import time
import random
import json
import requests
from src.config.config import CONFIG_FILE_PATH
from src.middleware.header_middleware import extract_bobb_headers
from src.helpers import find_best_route



UPDATE_LOCATION_ENDPOINT = "/update_location"

CITY_LIST = [
    "Valencia", "Madrid", "Barcelona", "Sevilla", "Zaragoza",
    "Málaga", "Murcia", "Palma de Mallorca", "Las Palmas de Gran Canaria", "Bilbao"
]

def simulate_satellite_operations(all_satellites: list):
    while True:
        try:
            satellite_id = random.choice(CITY_LIST)
            headers = extract_bobb_headers()
            satellite_ip = headers["dest_ipv4"]
            satellite_port = headers["dest_port"]

            port = os.getenv("PORT")

            config = None
            with open(CONFIG_FILE_PATH(port), "r") as config_file:
                config = json.load(config_file)


            new_location = {
                "city": satellite_id,
                "name": config["name"]
            }
            print(f"[{satellite_id}] New location: {new_location}")

            destination = random.choice(all_satellites)
            dest_ip, dest_port = destination["ip"], destination["port"]

            print(f"[{satellite_id}] Calculating best route to destination {dest_ip}:{dest_port}...")
            best_route = find_best_route(f"{satellite_ip}:{satellite_port}", f"{dest_ip}:{dest_port}")

            if not best_route:
                print(f"[{satellite_id}] No route found to the destination.")
                time.sleep(300)
                continue

            destination_url = f"https://{dest_ip}:{dest_port}{UPDATE_LOCATION_ENDPOINT}"
            response = requests.post(destination_url, json={"location": new_location, "route": best_route}, verify=False)

            if response.status_code == 200:
                print(f"[{satellite_id}] Location successfully updated to {dest_ip}:{dest_port}.")
            else:
                print(f"[{satellite_id}] Failed to update location: {response.status_code} - {response.text}")
                time.sleep(300)
                continue

            is_base_station = response.json().get("is_base_station", False)
            if is_base_station:
                print(f"[{satellite_id}] Base station recorded the location.")
            else:
                next_destination = response.json().get("next_destination")
                if next_destination:
                    next_ip, next_port = next_destination.split(":")
                    print(f"[{satellite_id}] Re-routing to next satellite {next_ip}:{next_port}...")
                    best_route = find_best_route(f"{satellite_ip}:{satellite_port}", next_destination)

                    if best_route:
                        next_url = f"http://{next_ip}:{next_port}{UPDATE_LOCATION_ENDPOINT}"
                        requests.post(next_url, json={"location": new_location, "route": best_route})
                    else:
                        print(f"[{satellite_id}] No alternative routes found.")
            
            time.sleep(300)

        except Exception as e:
            print(f"[{satellite_id}] Error occurred: {e}")
            time.sleep(300)

def load_satellites_and_base_stations(config_file: str):
    with open(config_file, "r") as f:
        config = json.load(f)
    satellites = config["satellites"]
    return satellites

if __name__ == "__main__":
    config_path = "resources/satellite_config.json"
    all_satellites = load_satellites_and_base_stations(config_path)

    threading.Thread(
        target=simulate_satellite_operations,
        args=(all_satellites,),
        daemon=True
    ).start()

    while True:
        time.sleep(1)
