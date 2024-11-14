import json
import logging
import os

from src.config.constants import SATELLITE_FUNCTION_DISASTER_IMAGING, SATELLITE_FUNCTION_WHALE_TRACKING, \
    SATELLITE_FUNCTION_WINDFARM_MONITORING, SATELLITE_FUNCTION_POST_FLOOD_SURVIVOR_DETECTION_AERIALDRONES
from src.helpers.name_generator import generate_name

CONFIG_FILE_PATH = "config/config.json"

valid_functions = {
    SATELLITE_FUNCTION_DISASTER_IMAGING,
    SATELLITE_FUNCTION_WHALE_TRACKING,
    SATELLITE_FUNCTION_WINDFARM_MONITORING,
    SATELLITE_FUNCTION_POST_FLOOD_SURVIVOR_DETECTION_AERIALDRONES
}

def load_from_config_file(function):
    # check if config file exists
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as config_file:
            return json.load(config_file)

    return create_config(function)

def create_config(function):
    if function in valid_functions:
        pass
    else:
        logging.error("Invalid satellite function")
        exit()

    print(f"Creating config with function: {function}")

    config = {
        "name": generate_name(port),
        "function": function
    }

    with open(CONFIG_FILE_PATH, "w") as config_file:
        json.dump(config, config_file)

    return config