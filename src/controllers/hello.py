from flask import jsonify, request


def hello():
    # user_id = request.args.get('id')
    # return jsonify({"message": f"User ID is {user_id}"})
    return jsonify("Hello!")
