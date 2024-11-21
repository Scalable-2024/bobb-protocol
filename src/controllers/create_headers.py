# Written by Vishaalini
from flask import jsonify, request
from src.utils.headers.necessary_headers import BobbHeaders
from src.utils.headers.optional_header import BobbOptionalHeaders

def create_header():
    # Get data from the request body
    body_data = request.get_json()

    try:
        # Extract necessary header fields
        necessary_header = body_data["necessary_header"]
        version_major = necessary_header["version_major"]
        version_minor = necessary_header["version_minor"]
        message_type = necessary_header["message_type"]
        dest_ipv4 = necessary_header["dest_ipv4"]
        dest_port = necessary_header["dest_port"]
        source_ipv4 = necessary_header["source_ipv4"]
        source_port = necessary_header["source_port"]
        sequence_number = necessary_header["sequence_number"]
        timestamp = necessary_header["timestamp"]

        # Generate the X-Bobb-Header
        bobb_header = BobbHeaders(
            version_major=version_major,
            version_minor=version_minor,
            message_type=message_type,
            dest_ipv4=dest_ipv4,
            dest_port=dest_port,
            source_ipv4=source_ipv4,
            source_port=source_port,
            sequence_number=sequence_number,
            timestamp=timestamp
        )
        x_bobb_header = bobb_header.build_header().hex()

        # Extract optional header fields
        optional_header = body_data["optional_header"]
        hop_count = optional_header["hop_count"]
        priority = optional_header["priority"]
        encryption_algo = optional_header["encryption_algo"]

        # Generate the X-Bobb-Optional-Header
        optional_header_obj = BobbOptionalHeaders(
            timestamp=timestamp,
            hop_count=hop_count,
            priority=priority,
            encryption_algo=encryption_algo
        )
        x_bobb_optional_header = optional_header_obj.build_optional_header().hex()

    except KeyError as e:
        return jsonify({
            "status": "error",
            "message": f"Missing required field: {e.args[0]}"
        }), 400

    # Return the headers in the response
    return jsonify({
        "status": "success",
        "data": {
            "X-Bobb-Header": x_bobb_header,
            "X-Bobb-Optional-Header": x_bobb_optional_header
        },
        "status_code": 200
    }), 200
