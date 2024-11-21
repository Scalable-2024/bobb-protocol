# Written by Niels
from flask import request

def capture_image():
    body_data = request.get_json()

    # TODO: add logic to check if this satellite should take the image
    # Check if this satellite is the satellite that can take images and should take the image
    # We have to wait for the implementation of the routing to further implement this

