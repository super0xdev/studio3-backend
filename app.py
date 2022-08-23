from solana_utils.verify_signature import verify_address_ownership
from flask import Flask, jsonify, make_response, request, session
from response_utils.response_codes import ResponseCodes
from response_utils.format_reponse import format_response
import traceback
import logging
import tables
import json
import time
import uuid
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/login", methods=['POST'])
def login():
    try:
        # extract arguments
        address = request.json['address']
        timestamp = request.json['timestamp']
        signature = request.json['signature'].encode()
        verify_address_ownership(address, timestamp, signature)

        # lookup user
        users = tables.Users.select(address=address)
        data = None
        if len(users) == 0:
            # crete new user
            user_uid = int(uuid.uuid4())
            _result = tables.Users.insert(uid=user_uid,
                                          address=address,
                                          creation_timestamp=int(time.time()),
                                          updated_timestamp=int(time.time()))
            response_code = ResponseCodes.NEW_REGISTRATION.value
        else:
            # return existing user
            response_code = ResponseCodes.LOGIN_SUCCESS.value
            user: tables.Users = users[0]
            user_uid = user.uid
            data = {"address": user.address, "user_uid": user_uid}

        # create session
        session['address'] = address
        session['user_uid'] = user_uid
        return format_response(True, response_code, data)

    except Exception as e:
        logging.error(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


@app.route("/update_profile", methods=['POST'])
def update_profile():
    if 'user_uid' in session:
        logging.info(f"got session with user_uid: {session['user_uid']}")
        return format_response(True, "AUTHENTICATED_WITH_SESSION_COOKIE_SUCCESS")
    else:
        return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)


########################################################################################################################
########################################################################################################################
########################################################################################################################


@app.route("/upload_asset", methods=['POST'])
def upload_asset():
    logging.info("inside upload_asset")
    try:
        # TODO parse metadata for name
        metadata = json.loads(request.files['metadata'].read())
        image = request.files['image'].read()
        # TODO make tmp file name
        with open('./tmp_upload/tes_tmp_0.jpg', 'wb') as f:
            f.write(image)
            logging.info(f"wrote tmp image")
        # TODO insert into database
        # TODO delete tmp file name
        logging.info(f"got metadata: {metadata}")
    except Exception as e:
        logging.error(e)
    return format_response(True, "TEST_CODE")


@app.route("/list_assets", methods=['POST'])
def list_assets():
    # TODO get uid from cookie
    pass


@app.route("/download_asset", methods=['POST'])
def download_asset():
    asset_uid = request.json['asset_uid']
    pass


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)




