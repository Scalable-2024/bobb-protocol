from flask import request, g
from src.utils.headers.necessary_headers import BobbHeaders
from src.utils.headers.optional_header import BobbOptionalHeaders
from src.helpers.response_helper import create_response


def check_headers():
    """
    Middleware to parse BobbHeaders and BobbOptionalHeaders from the request.
    """
    # Parse BobbHeaders
    custom_header = request.headers.get('X-Bobb-Header')
    if custom_header:
        try:
            bobb = BobbHeaders()
            g.bobb_header = bobb.parse_header(bytes.fromhex(custom_header))
        except Exception as e:
            return create_response({"error": "Invalid Bobb header", "details": str(e)}, 400)
    else:
        g.bobb_header = None

    # Parse BobbOptionalHeaders
    optional_header = request.headers.get('X-Bobb-Optional-Header')
    if optional_header:
        try:
            leo = BobbOptionalHeaders()
            g.bobb_optional_header = leo.parse_optional_header(
                bytes.fromhex(optional_header))
        except Exception as e:
            return create_response({"error": "Invalid Bobb optional header", "details": str(e)}, 400)
    else:
        g.bobb_optional_header = None

    # If headers are valid, allow request to proceed
    return None
