import time
from flask import Flask, request, g
from src.routers.__main__ import router as main_router
from src.utils.necessary_headers import BobbHeaders
from src.helpers.response_helper import create_response

app = Flask(__name__)

# Register routers
app.register_blueprint(main_router)


@app.before_request
def add_bob2_header_to_request():
    """
    Middleware to parse the custom BobbHeaders from the incoming request.
    """
    custom_header = request.headers.get('X-Bobb-Header')
    if custom_header:
        try:
            bob2 = BobbHeaders()
            g.bob2_header = bob2.parse_header(bytes.fromhex(
                custom_header))  # Store parsed header in `g`
        except Exception as e:
            return create_response({"error": "Invalid Bobb header", "details": str(e)}, 400)
    else:
        g.bob2_header = None  # No custom header present


@app.after_request
def add_bob2_header_to_response(response):
    """
    Middleware to inject the BobbHeaders into the response.
    """
    bob2_response = BobbHeaders(
        version_major=1,
        version_minor=0,
        message_type=2,
        sequence_number=456,
        timestamp=int(time.time())
    )
    response.headers['X-Bobb-Header'] = bob2_response.build_header().hex()
    return response


if __name__ == "__main__":
    app.run(debug=True)
