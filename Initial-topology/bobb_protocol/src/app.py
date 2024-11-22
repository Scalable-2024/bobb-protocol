# import time
# from flask import Flask, request, g
# from bobb_protocol.src.routers.__main__ import router as main_router
# from bobb_protocol.src.utils.headers.necessary_headers import BobbHeaders
# from bobb_protocol.src.utils.headers.optional_header import BobbOptionalHeaders
# from bobb_protocol.src.helpers.response_helper import create_response
# from bobb_protocol.src.config.constants import X_BOBB_HEADER, X_BOBB_OPTIONAL_HEADER, ERROR_INVALID_BOBB_HEADER, ERROR_INVALID_OPTIONAL_HEADER
#
# app = Flask(__name__)
#
# # Register routers
# app.register_blueprint(main_router)
#
#
# @app.before_request
# def add_custom_headers_to_request():
#     # Parse BobbHeaders
#     custom_header = request.headers.get(X_BOBB_HEADER)
#     if custom_header:
#         try:
#             bobb = BobbHeaders()
#             g.bobb_header = bobb.parse_header(bytes.fromhex(custom_header))
#         except Exception as e:
#             return create_response({"error": ERROR_INVALID_BOBB_HEADER, "details": str(e)}, 400)
#     else:
#         g.bobb_header = None  # No Bobb header present
#
#     # Parse LEOOptionalHeaders
#     optional_header = request.headers.get(X_BOBB_OPTIONAL_HEADER)
#     if optional_header:
#         try:
#             leo = BobbOptionalHeaders()
#             g.bobb_optional_header = leo.parse_optional_header(
#                 bytes.fromhex(optional_header))
#         except Exception as e:
#             return create_response({"error": X_BOBB_OPTIONAL_HEADER, "details": str(e)}, 400)
#     else:
#         g.bobb_optional_header = None  # No optional header present
#
#
# @app.after_request
# def add_custom_headers_to_response(response):
#     """
#     Middleware to inject the BobbHeaders and LEOOptionalHeaders into the response.
#     """
#     # Add BobbHeader to response
#     bobb_response = BobbHeaders(
#         version_major=1,
#         version_minor=0,
#         message_type=2,
#         sequence_number=456,
#         timestamp=int(time.time())
#     )
#     response.headers[X_BOBB_HEADER] = bobb_response.build_header().hex()
#
#     # Add LEOOptionalHeader to response
#     leo_response = BobbOptionalHeaders(
#         timestamp=int(time.time()),
#         hop_count=10,
#         priority=1,
#         encryption_algo="AES256"
#     )
#     response.headers[X_BOBB_OPTIONAL_HEADER] = leo_response.build_optional_header(
#     ).hex()
#
#     return response
#
#
# if __name__ == "__main__":
#     app.run(debug=True)

import os
import time
import logging
from flask import Flask, request, g
from bobb_protocol.src.routers.__main__ import router as main_router
from bobb_protocol.src.utils.headers.necessary_headers import BobbHeaders
from bobb_protocol.src.utils.headers.optional_header import BobbOptionalHeaders
from bobb_protocol.src.helpers.response_helper import create_response
from bobb_protocol.src.config.constants import X_BOBB_HEADER, X_BOBB_OPTIONAL_HEADER, ERROR_INVALID_BOBB_HEADER, ERROR_INVALID_OPTIONAL_HEADER

# 设置日志
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# 注册蓝图路由
app.register_blueprint(main_router)

# 配置拓扑文件路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
TOPOLOGY_FILE = os.path.join(PROJECT_ROOT, "topology.pkl")
print(f"Topology file path: {TOPOLOGY_FILE}")

@app.before_request
def add_custom_headers_to_request():
    # 解析 BobbHeaders
    custom_header = request.headers.get(X_BOBB_HEADER)
    if custom_header:
        try:
            bobb = BobbHeaders()
            g.bobb_header = bobb.parse_header(bytes.fromhex(custom_header))
        except Exception as e:
            return create_response({"error": ERROR_INVALID_BOBB_HEADER, "details": str(e)}, 400)
    else:
        g.bobb_header = None  # 没有 Bobb header

    # parse LEOOptionalHeaders
    optional_header = request.headers.get(X_BOBB_OPTIONAL_HEADER)
    if optional_header:
        try:
            leo = BobbOptionalHeaders()
            g.bobb_optional_header = leo.parse_optional_header(bytes.fromhex(optional_header))
        except Exception as e:
            return create_response({"error": ERROR_INVALID_OPTIONAL_HEADER, "details": str(e)}, 400)
    else:
        g.bobb_optional_header = None

@app.after_request
def add_custom_headers_to_response(response):
    """
    middleware to inject the BobbHeaders and LEOOptionalHeaders into the response.
    """
    # add BobbHeader to response
    bobb_response = BobbHeaders(
        version_major=1,
        version_minor=0,
        message_type=2,
        sequence_number=456,
        timestamp=int(time.time())
    )
    response.headers[X_BOBB_HEADER] = bobb_response.build_header().hex()

    # add LEOOptionalHeader to response
    leo_response = BobbOptionalHeaders(
        timestamp=int(time.time()),
        hop_count=10,
        priority=1,
        encryption_algo="AES256"
    )
    response.headers[X_BOBB_OPTIONAL_HEADER] = leo_response.build_optional_header().hex()

    return response

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)

