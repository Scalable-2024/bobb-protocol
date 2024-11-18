import json
import time

class SatelliteHandshake:
    def __init__(self, device_name, device_function, public_key, port):
        self.device_name = device_name
        self.device_function = device_function
        self.public_key = public_key
        self.port = port

    def build_message(self):
        # Build the main handshake message
        message = {
            "device_name": self.device_name,
            "device_function": self.device_function,
            "public_key": self.public_key,
            "port": self.port,
            "timestamp": int(time.time())
        }
        
        # Convert message dictionary to JSON string
        return json.dumps(message)

    def parse_message(self, json_data):
        # Parse a JSON-encoded message string to extract data
        parsed_data = json.loads(json_data)
        
        # Extract data into fields
        self.device_name = parsed_data.get("device_name")
        self.device_function = parsed_data.get("device_function")
        self.public_key = parsed_data.get("public_key")
        self.port = parsed_data.get("port")
        self.timestamp = parsed_data.get("timestamp")
        
        return parsed_data
