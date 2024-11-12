from flask import request
from src.helpers.response_helper import create_response
from src.routers.find_shortest_way import find_shortest_path
from src.config.constants import DEVICE_CONNECTION_PATH
def get_static_route():
    start_node = request.args.get('start_node')
    end_node = request.args.get('end_node')
    if not start_node or not end_node:
        return create_response({'error': 'Missing start_node or end_node'}, 400)
    path = find_shortest_path(DEVICE_CONNECTION_PATH, start_node, end_node)
    if path:
        return create_response({'path': path}, 200)
    else:
        return create_response({'error': 'No path found'}, 404)