from flask import g
from src.helpers.response_helper import create_response


def hello():
    # Access parsed Bob2Header from `g` (set by middleware)
    if g.bob2_header:
        header_data = g.bob2_header
    else:
        header_data = {"message": "No Bob2 header in request"}

    return create_response({"message": "Hello with Bob2 Header!", "header_data": header_data}, 200)
