# Written by Aryan, modified by Claire
from flask import jsonify
from typing import Any, Dict, Union, Optional

# import logging

# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

def create_response(data: Union[str, Dict[str, Any], list, tuple], status_code: int, headers: Optional[Dict[str, str]] = None) -> tuple:
    """
    Creates a standardized JSON response with optional headers.

    Parameters:
        data (Union[str, Dict[str, Any], list, tuple]): The data to include in the response.
        status_code (int): The HTTP status code for the response. Must be provided explicitly.
        headers (Optional[Dict[str, str]]): Optional headers to include in the response.

    Returns:
        tuple: A Flask JSON response, the associated status code, and headers if provided.
    """
    response_body = {
        "status": "success" if 200 <= status_code < 400 else "error",
        "data": data,
        "status_code": status_code
    }
    response = jsonify(response_body)
    response.status_code = status_code

    # Add headers if provided
    if headers:
        for key, value in headers.items():
            response.headers[key] = value

    # logger.info(response) if 200 <= status_code else logger.error(response)
    return response

