from solana_utils.verify_signature import verify_address_ownership
from flask import Flask, jsonify, make_response, request
from response_utils.response_codes import ResponseCodes
from response_utils.format_reponse import format_response
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
    return format_response(success, response_code)


@app.route("/upload_asset", methods=['POST'])
def upload_asset():
    logging.info("inside upload_asset")
    try:
        logging.info(f"got files: {request.files}")
        image = request.files['image'].read()
        with open('./tmp_upload/tes_tmp_0.jpg', 'wb') as f:
            f.write(image)
            logging.info(f"wrote tmp image")
        metadata = json.loads(request.files['metadata'].read())
        logging.info(f"got metadata: {metadata}")

    except Exception as e:
        logging.error(e)
    return format_response(True, "TEST_CODE")


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)




