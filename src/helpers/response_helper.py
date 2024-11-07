from flask import jsonify
from typing import Any, Dict, Union
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_response(data: Union[str, Dict[str, Any], list, tuple], status_code: int) -> tuple:
    """
    Creates a standardized JSON response.

    Parameters:
        data (Union[str, Dict[str, Any], list, tuple]): The data to include in the response. Can be a string, dictionary, list, or tuple.
        status_code (int): The HTTP status code for the response. Must be provided explicitly.

    Returns:
        tuple: A Flask JSON response and the associated status code.
    """
    response_body = {
        "status": "success" if 200 <= status_code < 400 else "error",
        "data": data,
        "status_code": status_code
    }
    json_data = jsonify(response_body), status_code
    logger.info(json_data) if 200 <= status_code else logger.error(
        json_data)
    return json_data
