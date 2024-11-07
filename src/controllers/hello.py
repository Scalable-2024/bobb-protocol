from src.helper.response_helper import create_response as Response


def hello():
    # user_id = request.args.get('id')
    # return jsonify({"message": f"User ID is {user_id}"})
    return Response("Hello", 200)
