import time
from flask import Flask, request, g
from src.routers.__main__ import router as main_router
from src.utils.headers.necessary_headers import BobbHeaders
from src.utils.headers.optional_header import BobbOptionalHeaders
from src.helpers.response_helper import create_response

app = Flask(__name__)

# Register routers
app.register_blueprint(main_router)


@app.before_request
def add_custom_headers_to_request():
    """
    Middleware to parse the custom BobbHeaders and LEOOptionalHeaders from the incoming request.
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
        g.bobb_header = None  # No Bobb header present

    # Parse LEOOptionalHeaders
    optional_header = request.headers.get('X-Bobb-Optional-Header')
    if optional_header:
        try:
            leo = BobbOptionalHeaders()
            g.bobb_optional_header = leo.parse_optional_header(
                bytes.fromhex(optional_header))
        except Exception as e:
            return create_response({"error": "Invalid LEO optional header", "details": str(e)}, 400)
    else:
        g.bobb_optional_header = None  # No optional header present


@app.after_request
def add_custom_headers_to_response(response):
    """
    Middleware to inject the BobbHeaders and LEOOptionalHeaders into the response.
    """
    # Add BobbHeader to response
    bobb_response = BobbHeaders(
        version_major=1,
        version_minor=0,
        message_type=2,
        sequence_number=456,
        timestamp=int(time.time())
    )
    response.headers['X-Bobb-Header'] = bobb_response.build_header().hex()

    # Add LEOOptionalHeader to response
    leo_response = BobbOptionalHeaders(
        timestamp=int(time.time()),
        hop_count=10,
        priority=1,
        encryption_algo="AES256"
    )
    response.headers['X-Bobb-Optional-Header'] = leo_response.build_optional_header().hex()

    return response


if __name__ == "__main__":
    app.run(debug=True)
