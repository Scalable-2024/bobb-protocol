from src.helpers.response_helper import create_response
from src.config.config import CONFIG_FILE_PATH
import os
import json

def return_identity():
    port = os.getenv("PORT")
    try:
        with open(CONFIG_FILE_PATH(port), "r") as config:
            config = json.load(config)
            function = config["function"]
            return create_response(function, 200)
    except FileNotFoundError:
        create_response("Device function not configured on server", 500)
