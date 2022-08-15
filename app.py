from solana_utils.verify_signature import verify_address_ownership
from flask import Flask, jsonify, make_response, request
from constants.response_codes import ResponseCodes
import traceback
import logging
import tables
import json
import time
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


@app.route("/login", methods=['POST'])
def login():
    try:
        address = request.json['address']
        timestamp = request.json['timestamp']
        signature = request.json['signature'].encode()
        verify_address_ownership(address, timestamp, signature)
        logging.info(f"SIGNATURE IS VALID")
        # check if exists
        users = tables.Users.select(address=address)
        if len(users) == 0:
            _result = tables.Users.insert(address=address,
                                          creation_timestamp=int(time.time()),
                                          updated_timestamp=int(time.time()))
            response_code = ResponseCodes.NEW_REGISTRATION.value
        else:
            response_code = ResponseCodes.LOGIN_SUCCESS.value
        success = True
    except Exception as e:
        logging.error(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        success = False
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"success": success, 'code': response_code})
    }
    return response


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

