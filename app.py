from solana_utils.verify_signature import verify_address_ownership
from flask import Flask, jsonify, make_response, request, session, send_file
from response_utils.response_codes import ResponseCodes
from response_utils.format_reponse import format_response
import traceback
from s3_utils.upload_asset import upload_asset
from s3_utils.download_asset import download_asset
import logging
import os
import tables
import time
import random
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
        logging.info(f"verified ownership of address: {address}")

        # lookup user
        users = tables.Users.select(address=address)
        data = None
        if len(users) == 0:
            # crete new user
            user_uid = random.randint(int(2**60), int(2**64)-1)
            logging.info(f"generated new uid: {user_uid}")
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
            data = {"address": str(user.address), "user_uid": user_uid, 'username': user.username, 'email': user.email}

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
        user_uid = session['user_uid']
        # extract update values
        values = {}
        username = request.json['username']
        email = request.json['email']
        if username:
            values['username'] = username
        if email:
            values['email'] = email
        # update profile
        _result = tables.Users.update(values, uid=user_uid)
        return format_response(True, ResponseCodes.USER_PROFILE_UPDATE_SUCCESS.value, values)
    else:
        return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)


@app.route("/upload_asset", methods=['POST'])
def handle_upload_asset():
    logging.info("inside upload_asset")
    try:
        if 'user_uid' in session:
            user_uid = session['user_uid']

            image_file = request.files['image']
            file_name = image_file.filename
            file_type = file_name.split(".")[1]
            image_bytes = request.files['image'].read()
            image_size_bytes = len(image_bytes)

            logging.info(f"got files: {request.files}")
            logging.info(f"got filename: {file_name}")
            logging.info(f"got image size bytes: {image_size_bytes}")
            logging.info(f"got file type: {file_type}")

            tmp_fname = f"tmp_{int(time.time())}_{file_name}"
            tmp_fpath = os.path.join('/tmp', tmp_fname)
            with open(tmp_fpath, 'wb') as f:
                f.write(image_bytes)
                logging.info(f"wrote tmp image: {tmp_fpath}")

            file_key = upload_asset(tmp_fpath, tmp_fname)
            logging.info(f"uploaded to se with file key: {file_key}")
            os.remove(tmp_fpath)
            logging.info(f"deleted tmp file: {tmp_fpath}")

            _result = tables.Assets.insert(file_path=file_key,
                                           file_type=file_type,
                                           file_name=file_name,
                                           file_size_bytes=image_size_bytes,
                                           creation_timestamp=int(time.time()),
                                           user_uid=user_uid)
            logging.info(f"inserted into table with result: {_result}")
            return format_response(True, ResponseCodes.UPLOAD_SUCCESS.value)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        logging.error(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


@app.route("/list_assets", methods=['POST'])
def list_assets():
    try:
        if 'user_uid' in session:
            user_uid = session['user_uid']
            assets = tables.Assets.select(user_uid=user_uid)
            logging.info(f"got assets: {assets}")
            asset_dicts = [x.to_dict() for x in assets]
            return format_response(True, ResponseCodes.LIST_SUCCESS.value, data=asset_dicts)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        logging.error(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


@app.route("/download_asset", methods=['POST'])
def handle_download_asset():
    if 'user_uid' in session:
        file_key = request.json['file_path']
        logging.info(f"got filekey in requeast: {file_key}")
        tmp_fpath = download_asset(file_key)
        logging.info(f"downloaded to tmp fpath: {tmp_fpath}")
        return send_file(tmp_fpath)
    else:
        return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)




