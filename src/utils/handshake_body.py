import json

class SatelliteHandshake:
    def __init__(self, satellite_function, public_key, connected_nodes=None):
        self.satellite_function = satellite_function
        self.public_key = public_key
        self.connected_nodes = connected_nodes if connected_nodes is not None else []

    def build_message(self):
        # Build the main handshake message
        message = {
            "satellite_function": self.satellite_function,
            "public_key": self.public_key,
            "connected_nodes": [
                {
                    "satellite_function": node["satellite_function"],
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
        self.satellite_function = parsed_data.get("satellite_function")
        self.public_key = parsed_data.get("public_key")
        self.connected_nodes = parsed_data.get("connected_nodes", [])
        
        return parsed_data
