from flask import make_response, jsonify


def format_response(success, response_code, data=None):
    message = {"success": success, 'code': response_code, "data": data}
    response = make_response(jsonify(message), 200)
    # response.headers['Access-Control-Allow-Origin'] = "http://127.0.0.1:3000"
    response.headers['Access-Control-Allow-Origin'] = "*"
    # response.headers['Access-Control-Allow-Credentials'] = "true"
    return response
