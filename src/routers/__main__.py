import csv
import random
from flask import Blueprint, app, jsonify, request  # Add request here
import base64
import json
import os

from flask import Blueprint, app, jsonify
import requests

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


@router.route("/call_satellite_from_whale", methods=["POST"])
def call_satellite_from_whale():
    """
    Route a message between satellites.
    Expected POST body: {
        "source": "ip:port",
        "destination": "ip:port",
        "message": "message content",
        "hops": [list of already visited satellites] (optional)
    }
    """
    middleware_response = check_headers()
    if middleware_response is not True:
        return middleware_response

    try:
        data = request.json
        source = data["source"]
        destination = data["destination"]
        message = data["message"]
        # Track hops to prevent infinite forwarding
        hops = data.get("hops", [])

        # Get current satellite info
        current_port = os.getenv("PORT")
        current_ip = os.getenv("IP")
        current_satellite = f"{current_ip}:{current_port}"

        if destination == current_satellite:
            print("ARRIVEDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"*100)
            return

        # If we've already been here, stop
        if current_satellite in hops:
            return jsonify({
                "status": "error",
                "message": "Forwarding loop detected",
                "status_code": 400
            }), 400

        # If we've reached max hops, stop
        if len(hops) >= 5:  # Limit to 5 hops
            return jsonify({
                "status": "error",
                "message": "Max hop limit reached",
                "status_code": 400
            }), 400

        # Add current satellite to hops
        hops.append(current_satellite)

        # Read satellite listings file
        listings_file = f"resources/satellite_listings/full_satellite_listing_{current_port}.csv"
        available_satellites = []

        with open(listings_file, 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                satellite_id = f"{row['IPv4']}:{row['Port']}"
                if satellite_id not in hops:  # Only add satellites we haven't visited
                    available_satellites.append(satellite_id)

        if not available_satellites:
            return jsonify({
                "status": "error",
                "message": "No available satellites found",
                "status_code": 404
            }), 404

        # Choose random satellite
        random_satellite = random.choice(available_satellites)

        try:
            # Forward the request to random satellite with timeout
            forward_response = requests.post(
                f"https://{random_satellite}/call_satellite_from_whale",
                json={
                    "source": source,
                    "destination": destination,
                    "message": message,
                    "hops": hops  # Include hop history
                },
                headers={
                    'Content-Type': 'application/json',
                    'X-Bobb-Header': request.headers.get('X-Bobb-Header')
                },
                verify=False,
                proxies={'http': '', 'https': ''},
                timeout=5  # 5 second timeout
            )

            return jsonify({
                "status": "success",
                "data": {
                    "forwarded_to": random_satellite,
                    "forward_response": forward_response.json(),
                    "hops": hops
                },
                "status_code": 200
            }), 200

        except requests.Timeout:
            return jsonify({
                "status": "error",
                "message": f"Timeout while forwarding to {random_satellite}",
                "status_code": 408
            }), 408
        except requests.RequestException as e:
            return jsonify({
                "status": "error",
                "message": f"Error forwarding to {random_satellite}: {str(e)}",
                "status_code": 500
            }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error processing request: {str(e)}",
            "status_code": 500
        }), 500

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
    middleware_response = check_headers()
    if middleware_response is not True:
        return middleware_response  # Return error if headers are invalid
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
