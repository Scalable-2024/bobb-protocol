import base64
import json
import os
import random

import requests

from src.config.constants import SATELLITE_FUNCTION_DISASTER_IMAGING, X_BOBB_HEADER
from src.routing.find_best_route import find_best_route
from src.utils.headers.necessary_headers import BobbHeaders

CITY_LIST = [
    "Tokyo",
    "Delhi",
    "Shanghai",
    "Valencia",
    "Mumbai",
    "Beijing",
    "New York",
    "Moscow",
    "Cairo",
    "Bangkok",
    "Los Angeles",
    "Buenos Aires",
    "Istanbul",
    "Kolkata",
    "Rio de Janeiro",
    "Lagos",
    "Paris"
]

def get_random_city():
    return random.choice(CITY_LIST)

def get_random_basestation(port):

    with open(f"resources/satellite_constellation_set/constellation_{port}.json", "r") as f:
        data = json.load(f)
        f.close()

    base_stations = []

    for key, value in data.items():
        neighbours = value.get("neighbours", {})
        for neighbour_key, neighbour_value in neighbours.items():
            if neighbour_value.get("function") == "basestation":
                base_stations.append({
                    "ip": neighbour_value["ip"],
                    "port": neighbour_value["port"],
                    "address": neighbour_key,
                    "function": neighbour_value["function"],
                    "public_key": neighbour_value["public_key"]
                })

    return random.choice(base_stations)

def send_disaster_relieve_message():
    device_function = os.getenv("DEVICE_FUNCTION")
    # print(device_function)

    if device_function != SATELLITE_FUNCTION_DISASTER_IMAGING:
        # print(f"Device function is {device_function}: {SATELLITE_FUNCTION_DISASTER_IMAGING}")
        # print("Not a disaster imaging satellite")
        return

    city = get_random_city()
    print(f"Taking image of {city}")

    basestation = get_random_basestation(os.getenv("PORT"))
    print(basestation)

    source_ip = os.getenv("IP")
    source_port = os.getenv("PORT")
    header = BobbHeaders(message_type=1, source_ipv4=source_ip,
                source_port=int(source_port), dest_ipv4=basestation["ip"], dest_port=int(basestation["port"])).build_header().hex()

    route_info = find_best_route(f"{source_ip}:{source_port}", f"{basestation['ip']}:{basestation['port']}", "high")
    if not route_info:
        print("No route found")
        return

    headers = {
        X_BOBB_HEADER: header,
    }

    with open("src/helpers/Valencia_Spain.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        image_file.close()

    request = {
        "disaster_needs": {
            "location": city,
            "image": encoded_string,
            "essentials": {
                "food": {
                    "non_perishable": ["canned goods", "dried fruits", "protein bars"],
                    "baby_food": ["infant formula", "baby cereal"]
                },
                "water": {
                    "bottled_water": "Minimum 1 gallon per person per day",
                    "water_purification": ["water filters", "purification tablets"]
                },
                "clothing": ["warm clothing", "rain gear", "sturdy shoes"]
            },
            "medical_supplies": {
                "first_aid_kit": [
                    "bandages",
                    "antiseptic wipes",
                    "pain relievers",
                    "gauze",
                    "medical tape"
                ],
                "prescription_medications": "30-day supply if possible",
                "personal_hygiene": [
                    "toothbrush and toothpaste",
                    "soap",
                    "hand sanitizer",
                    "feminine hygiene products"
                ]
            },
            "shelter": {
                "emergency_shelter": ["tents", "tarps", "thermal blankets"],
                "tools": ["multi-tool", "duct tape", "rope"]
            },
            "communication": {
                "devices": ["battery-powered radio", "cell phones"],
                "charging": ["power banks", "solar chargers"],
                "contacts": ["emergency numbers", "family contact list"]
            },
            "emergency_equipment": {
                "lighting": ["flashlights", "lanterns", "extra batteries"],
                "tools": ["fire extinguisher", "crowbar", "shovel"]
            },
            "documents": {
                "identification": ["passports", "driver's licenses"],
                "important_papers": ["insurance documents", "medical records"],
                "emergency_plan": "A printed copy of the family emergency plan"
            },
            "miscellaneous": {
                "cash": "Small denominations for emergency purchases",
                "entertainment": ["books", "games for children"],
                "pets": ["pet food", "collar and leash", "vaccination records"]
            }
        }
    }

    json_output = json.dumps(request)

    print(json_output)

    print(f"Sending disaster relieve message to {basestation['ip']}:{basestation['port']}")
    response = requests.post(f"https://{route_info['path'][0]}/image", headers=headers, verify=False, json=json_output)
    print(response.status_code)
