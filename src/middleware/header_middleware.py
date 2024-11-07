from flask import request, g
from src.utils.headers.necessary_headers import BobbHeaders
from src.utils.headers.optional_header import BobbOptionalHeaders
from src.helpers.response_helper import create_response
from src.config.constants import (
    X_BOBB_HEADER,
    X_BOBB_OPTIONAL_HEADER,
    ERROR_INVALID_BOBB_HEADER,
    ERROR_INVALID_OPTIONAL_HEADER
)


def check_headers():
    """
    Middleware to parse BobbHeaders and BobbOptionalHeaders from the request.
    """
    # Parse BobbHeaders
    custom_header = request.headers.get(X_BOBB_HEADER)
    if custom_header:
        try:
            bobb = BobbHeaders()
            g.bobb_header = bobb.parse_header(bytes.fromhex(custom_header))
        except Exception as e:
            return create_response({"error": ERROR_INVALID_BOBB_HEADER, "details": str(e)}, 400)
    else:
        g.bobb_header = None

    # Parse BobbOptionalHeaders
    optional_header = request.headers.get(X_BOBB_OPTIONAL_HEADER)
    if optional_header:
        try:
            leo = BobbOptionalHeaders()
            g.bobb_optional_header = leo.parse_optional_header(
                bytes.fromhex(optional_header)
            )
        except Exception as e:
            return create_response({"error": ERROR_INVALID_OPTIONAL_HEADER, "details": str(e)}, 400)
    else:
        g.bobb_optional_header = None

    # Print parsed headers for debugging
    print(f"Bobb Header: {g.bobb_header}")
    print(f"Bobb Optional Header: {g.bobb_optional_header}")

    # If headers are valid, allow request to proceed
    return None
