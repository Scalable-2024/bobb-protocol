import argparse
import logging
import time
import threading
import os
from flask import Flask, request, g
from src.config.config import load_from_config_file
from src.heartbeat.heartbeat import send_heartbeat_to_neighbours
from src.routers.__main__ import router as main_router
from src.utils.crypto_utils import generate_keys
from src.utils.headers.necessary_headers import BobbHeaders
from src.utils.headers.optional_header import BobbOptionalHeaders
from src.helpers.response_helper import create_response
from src.config.constants import X_BOBB_HEADER, X_BOBB_OPTIONAL_HEADER, ERROR_INVALID_BOBB_HEADER, ERROR_INVALID_OPTIONAL_HEADER
from src.discovery.discovery import get_neighbouring_satellites
from src.helpers.send_handshake_helper import send_handshakes
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

device_function = os.getenv("DEVICE_FUNCTION")
port = int(os.getenv("PORT"))

name = load_from_config_file(device_function, port)["name"]
generate_keys(name)

app = Flask(__name__)

# Register routers
app.register_blueprint(main_router)

scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def initial_satellite_search():
    time.sleep(2)
    print("Initial satellite search")
    get_neighbouring_satellites()

def schedule_activities_once_started_up():
    # Wait 4s to allow initial startup and discovery
    time.sleep(3)

    # Schedule satellite discovery every 5 minutes
    scheduler.add_job(func=get_neighbouring_satellites, trigger=IntervalTrigger(minutes=5), id='device_discovery', replace_existing=True)

    # Schedule handshaking every 30s
    scheduler.add_job(func=send_handshakes, trigger=IntervalTrigger(seconds=30), id='sending_handshakes', replace_existing=True)

    # Schedule heartbeat every 30s
    scheduler.add_job(func=send_heartbeat_to_neighbours, trigger=IntervalTrigger(seconds=30), id='sending_heartbeats', replace_existing=True)

thread = threading.Thread(target=initial_satellite_search)
thread.start()

schedule_thread = threading.Thread(target=schedule_activities_once_started_up)
schedule_thread.start()

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
    if X_BOBB_HEADER not in response.headers:
        # Add BobbHeader to response
        bobb_response = BobbHeaders(
            version_major=1,
            version_minor=0,
            message_type=2,
            sequence_number=456,
            timestamp=int(time.time())
        )
        response.headers[X_BOBB_HEADER] = bobb_response.build_header().hex()

    if X_BOBB_OPTIONAL_HEADER not in response.headers:
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
    parser = argparse.ArgumentParser(
        description="Bobb Satellite Parser")

    parser.add_argument('--function', type=str, help='Satellite function')
    parser.add_argument('--port', type=int, help='Port number')
    args = parser.parse_args()

    if not args.function:
        exit("Satellite function not provided")

    name = load_from_config_file(args.function, args.port)["name"]
    generate_keys(name)
    app.run(debug=True, port=args.port)
