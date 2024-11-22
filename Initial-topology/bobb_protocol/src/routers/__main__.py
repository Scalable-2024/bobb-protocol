# # routers/__main__.py
# from flask import Blueprint
#
# from bobb_protocol.src.controllers.create_headers import create_header
# from bobb_protocol.src.controllers.hello import hello
# from bobb_protocol.src.controllers.identify import return_identity
# from bobb_protocol.src.middleware.header import check_headers
#
# router = Blueprint('main', __name__)
#
# @router.route('/', methods=['GET'])
# def root():
#     middleware_response = check_headers()
#     if middleware_response is not True:
#         return middleware_response  # Return error if headers are invalid
#
#     # Call controller function if headers are valid
#     return hello()
#
# @router.route('/id', methods=['GET'])
# def identify():
#     return return_identity()
#
# @router.route('/create-header', methods=['POST'])
# def create_custom_headers():
#     return create_header()

# routers/__main__.py
from flask import Blueprint, request, jsonify
from bobb_protocol.src.routers.routing import find_shortest_path
import os

router = Blueprint('main', __name__)

@router.route('/shortest-path', methods=['GET'])
def shortest_path():
    source = request.args.get('source')
    target = request.args.get('target')
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    topology_file = os.path.join(project_root, "topology.pkl")  # 读取拓扑文件的路径

    if not source or not target:
        return jsonify({"error": "Source and target parameters are required"}), 400

    path = find_shortest_path(topology_file, source, target)
    if path is None:
        return jsonify({"error": "No path found"}), 404

    return jsonify({"path": path}), 200
