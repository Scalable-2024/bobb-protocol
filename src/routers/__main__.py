from flask import Blueprint, request
from src.controllers.hello import hello, hello_post
from src.middleware.header_middleware import check_headers

router = Blueprint('main', __name__)



@router.route('/', methods=['GET'])
def root():
    middleware_response = check_headers()
    if middleware_response is not True:
        return middleware_response  # Return error if headers are invalid

    # Call controller function if headers are valid
    return hello()

@router.route('/', methods=['POST'])
def root_post():
    middleware_response = check_headers()
    if middleware_response is not True:
        return middleware_response  # Return error if headers are invalid

    # Process POST data if headers are valid
    data = request.json  # Access the JSON payload sent with the POST request
    return hello_post() 