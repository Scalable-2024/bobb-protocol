import json

class SatelliteHandshake:
    def __init__(self, device_name, device_function, public_key, port, connected_nodes=None):
        self.device_name = device_name
        self.device_function = device_function
        self.public_key = public_key
        self.port = port
        self.connected_nodes = connected_nodes if connected_nodes is not None else []

    def build_message(self):
        # Build the main handshake message
        message = {
            "device_name": self.device_name,
            "device_function": self.device_function,
            "public_key": self.public_key,
            "port": self.port,
            "connected_nodes": [
                {
                    "device_function": node["device_function"],
                    "public_key": node["public_key"],
                    "connected_nodes": []  # Set to empty for connected nodes
                }
                for node in self.connected_nodes
            ]
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
        self.connected_nodes = parsed_data.get("connected_nodes", [])
        
        return parsed_data
