import os
import json
from flask import request, g
from src.helpers.response_helper import create_response
from src.utils.handshake_body import SatelliteHandshake
from src.utils.headers.necessary_headers import BobbHeaders
from src.config.constants import X_BOBB_HEADER
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
    own_public_key = "" # TODO add own public key here
    own_function = "undefined" # TODO add own function here
    return_handshake_body, headers = create_handshake_message(own_function, own_public_key, own_port, own_ip)

    return create_response(return_handshake_body, 200, headers=headers)

