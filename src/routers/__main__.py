from flask import Blueprint, app, jsonify, request  # Add request here
import base64
import json
import os

from flask import Blueprint, app, jsonify

from src.config.constants import SATELLITE_FUNCTION_DISASTER_IMAGING, BASESTATION
from src.controllers.create_headers import create_header
from src.controllers.hello import hello
from src.controllers.identify import return_identity
from src.controllers.handshake import handshake
from src.heartbeat.heartbeat import heartbeat
from src.middleware.header_middleware import check_headers
from enum import Enum
from typing import Dict, List, Optional, Tuple
from src.routing.find_best_route import find_best_route



router = Blueprint('main', __name__)


# In routers/__main__.py

# Add this import at the top with your other imports


class RouteType(Enum):
    DIRECT = 4
    FUNCTION = 3
    BALANCED = 2
    RANDOM = 1


@router.route('/route', methods=['POST'])
def route_message():
    """
    Route a message between satellites.
    Expected POST body: {
        "source": "ip:port",
        "destination": "ip:port",
        "message": "message content",
        "priority": "high/medium/low" (optional)
    }
    """
    try:
        body = request.get_json()

        # Validate request body
        if not all(k in body for k in ["source", "destination", "message"]):
            return jsonify({
                "status": "error",
                "message": "Missing required fields: source, destination, message",
                "status_code": 400
            }), 400

        source = body["source"]
        destination = body["destination"]
        message = body["message"]
        priority = body.get("priority", "medium")

        # Get route based on priority and weights
        route_info = find_best_route(source, destination, priority)

        if not route_info:
            return jsonify({
                "status": "error",
                "message": f"No route found between {source} and {destination}",
                "status_code": 404
            }), 404

        return jsonify({
            "status": "success",
            "data": {
                "source": source,
                "destination": destination,
                "selected_route": route_info["path"],
                "route_type": route_info["type"],
                "route_metrics": route_info["metrics"],
                "routing_table": route_info["routing_table"]
            },
            "status_code": 200
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error processing route request: {str(e)}",
            "status_code": 500
        }), 500




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
