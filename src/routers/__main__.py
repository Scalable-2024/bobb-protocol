from flask import Blueprint
from src.controllers.hello import hello
from src.middleware.header_middleware import check_headers

router = Blueprint('main', __name__)



@router.route('/', methods=['GET'])
def root():
    middleware_response = check_headers()
    if middleware_response is not True:
        return middleware_response  # Return error if headers are invalid

    # Call controller function if headers are valid
    return hello()
