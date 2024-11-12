import time
import threading
import os
import csv
from flask import Flask, request, g
from src.routers.__main__ import router as main_router
from src.utils.headers.necessary_headers import BobbHeaders
from src.utils.headers.optional_header import BobbOptionalHeaders
from src.helpers.response_helper import create_response
from src.config.constants import X_BOBB_HEADER, X_BOBB_OPTIONAL_HEADER, ERROR_INVALID_BOBB_HEADER, ERROR_INVALID_OPTIONAL_HEADER
from src.discovery.discovery import get_neighbouring_satellites
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

app = Flask(__name__)

# Register routers
app.register_blueprint(main_router)

scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# Schedule satellite discovery every 5 minutes
scheduler.add_job(func=get_neighbouring_satellites, trigger=IntervalTrigger(minutes=5), id='scheduled_task', replace_existing=True)

def initial_satellite_search():
    time.sleep(2)
    get_neighbouring_satellites()

thread = threading.Thread(target=initial_satellite_search)
thread.start()

@app.before_request
def add_custom_headers_to_request():
    # Parse BobbHeaders
    custom_header = request.headers.get(X_BOBB_HEADER)
    if custom_header:
        try:
            bobb = BobbHeaders()
            g.bobb_header = bobb.parse_header(bytes.fromhex(custom_header))
        except Exception as e:
            return create_response({"error": ERROR_INVALID_BOBB_HEADER, "details": str(e)}, 400)
    else:
        g.bobb_header = None  # No Bobb header present

    # Parse LEOOptionalHeaders
    optional_header = request.headers.get(X_BOBB_OPTIONAL_HEADER)
    if optional_header:
        try:
            leo = BobbOptionalHeaders()
            g.bobb_optional_header = leo.parse_optional_header(
                bytes.fromhex(optional_header))
        except Exception as e:
            return create_response({"error": X_BOBB_OPTIONAL_HEADER, "details": str(e)}, 400)
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
    response.headers[X_BOBB_HEADER] = bobb_response.build_header().hex()

    # Add LEOOptionalHeader to response
    leo_response = BobbOptionalHeaders(
        timestamp=int(time.time()),
        hop_count=10,
        priority=1,
        encryption_algo="AES256"
    )
    response.headers[X_BOBB_OPTIONAL_HEADER] = leo_response.build_optional_header(
    ).hex()

    return response


if __name__ == "__main__":
    app.run(debug=True)
    
