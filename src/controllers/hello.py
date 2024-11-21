# Written by Aryan
# from flask import g
from src.helpers.response_helper import create_response


def hello():
    # # Correct attribute name: bobb_header
    # bobb_header_data = g.bobb_header or {
    #     "message": "No Bobb header in request"}
    # bobb_optional_data = g.bobb_optional_header or {
    #     "message": "No Bobb optional header in request"}

    return create_response({
        "message": "Hello from Bobb Protocol!",
    }, 200)
