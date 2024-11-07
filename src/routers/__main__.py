from flask import Blueprint
from src.controllers.hello import hello
from src.middleware.header_middleware import check_headers

router = Blueprint('main', __name__)


@router.route('/', methods=['GET'])
def root():
    # Call middleware to check headers before executing the controller
    middleware_response = check_headers()
    if middleware_response:
        return middleware_response  # Return early if headers are invalid

    return hello()  # Call the controller function
