import base64
import os

from flask import Blueprint, app, jsonify, request

from src.config.constants import SATELLITE_FUNCTION_DISASTER_IMAGING, BASESTATION
from src.controllers.create_headers import create_header
from src.controllers.hello import hello
from src.controllers.identify import return_identity
from src.controllers.handshake import handshake
from src.heartbeat.heartbeat import heartbeat
from src.middleware.header_middleware import check_headers
from src.discovery.discovery import get_random_city

router = Blueprint('main', __name__)

@router.route('/', methods=['GET'])
def root():
    middleware_response = check_headers()
    if middleware_response is not True:
        return middleware_response  # Return error if headers are invalid

    # Call controller function if headers are valid
    return hello()

@router.route('/id', methods=['GET'])
def identify():
    return return_identity()

@router.route('/create-header', methods=['POST'])
def create_custom_headers():
    return create_header()

@router.route('/handshake', methods=['POST'])
def receive_handshake():
    middleware_response = check_headers()
    if middleware_response is not True:
        return middleware_response  # Return error if headers are invalid

    # Call controller function if headers are valid
    return handshake()

@router.route('/heartbeat', methods=["POST"])
def receive_heartbeat():
    middleware_response = check_headers()
    if middleware_response is not True:
        return middleware_response  # Return error if headers are invalid

    # Call controller function if headers are valid
    return heartbeat()

    @router.route('/send-location', methods=["POST"])
def send_location():
    """
    Randomly select and send location to the base station.
    """
    middleware_response = check_headers()
    if middleware_response is not True:
        return middleware_response  # Return error if headers are invalid

    try:
        location = get_random_city()
        base_station_url = "http://basestation.example.com/update-location"
        print(f"Sending location '{location}' to Base Station at {base_station_url}")
        return jsonify({"status": "success", "location_sent": location}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
# Base station routes

# @router.route('/v1/satellites', methods=['GET'])
# def get_satellites():
#     device_function = os.getenv("DEVICE_FUNCTION")
#     if device_function != BASESTATION:
#         return {
#             "error": "Only base stations can take images",
#             "status": "failure",
#             "status_code": 400
#         }, 400
#
#     satellites = read_satellites_from_json()
#     return {"satellites": satellites}
#
# @router.route('/v1/satellites/<string:ip>/images', methods=['POST'])
# def capture_image(ip):
#     device_function = os.getenv("DEVICE_FUNCTION")
#     if device_function != BASESTATION:
#         return {
#             "error": "Only base stations can take images",
#             "status": "failure",
#             "status_code": 400
#         }, 400
#
#     satellites = read_satellites_from_json()
#
#     if ip not in [sat["ip"] for sat in satellites]:
#         return {"error": "Satellite not found"}, 404
#
#     satellite = next((sat for sat in satellites if sat["ip"] == ip), None)
#     if satellite["function"] != SATELLITE_FUNCTION_DISASTER_IMAGING:
#         return {
#             "error": "Satellite can not take images",
#             "status": "failure",
#             "status_code": 400
#         }, 400
#
#     with open("development/mar-menor.jpg", "rb") as image_file:
#         base64_bytes = base64.b64encode(image_file.read())
#         encoded_string = base64_bytes.decode()
#
#     return {"status":"success","image": encoded_string, "status_code": 200}
