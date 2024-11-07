from flask import jsonify
from typing import Any, Dict, Union


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
    return jsonify(response_body), status_code
