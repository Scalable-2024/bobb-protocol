import requests
import os

BASESTATION_URL = os.getenv("BASESTATION_URL", "https://basestation.example.com")

def send_location(location_data):
    """Send the satellite's location to the basestation."""
    url = f"{BASESTATION_URL}/update-location"
    payload = {
        "satellite_name": location_data.get("name"),
        "location": location_data.get("location"),
        "ip": location_data.get("ip"),
        "function": location_data.get("function")
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        print(f"Location sent successfully: {response.json()}")
    except requests.RequestException as e:
        print(f"Failed to send location: {e}")
