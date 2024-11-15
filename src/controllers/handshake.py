import os
import json
from flask import request, g
from src.helpers.response_helper import create_response
from src.utils.handshake_body import SatelliteHandshake
from src.utils.headers.necessary_headers import BobbHeaders
from src.config.constants import X_BOBB_HEADER
from src.config.config import CONFIG_FILE_PATH
from src.helpers.general_handshake_helper import create_handshake_message, write_received_handshake


def handshake():
    handshake_data = request.get_json()
    bobb_header = g.bobb_header
    return handle_handshake(handshake_data, bobb_header)

def handle_handshake(handshake_data, bobb_header):
    print("About to receive handshakes")
    write_received_handshake(handshake_data, bobb_header)

    # Send handshake back
    own_ip = os.getenv("IP")
    own_port = int(os.getenv("PORT"))
    with open(CONFIG_FILE_PATH(own_port), "r") as config_file:
        config = json.load(config_file)
        name = config["name"]
        function = config["function"]
        public_key_path = os.path.join("keys", f"{name}_public_key.pem")
        with open(public_key_path, "r") as public_key_file:
            public_key = public_key_file.read()
            return_handshake_body, headers = create_handshake_message(name, function, public_key, own_port, own_ip)
            return create_response(return_handshake_body, 200, headers=headers)

