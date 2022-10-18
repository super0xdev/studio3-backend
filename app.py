from solana_utils.verify_signature import verify_address_ownership
from flask import Flask, jsonify, make_response, request, send_file
from flask_cors import CORS
from response_utils.response_codes import ResponseCodes
from response_utils.format_reponse import format_response
import traceback
from s3_utils.upload_asset import upload_asset
from s3_utils.download_asset import download_asset
from conf import consts as consts
from functools import wraps
import logging
import datetime
import os
import tables
import json
import time
import jwt
import random
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = consts.JWT_SECRET_KEY
CORS(app)


########################################################################################################################
########################################################################################################################
# Authentication
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        print(f"inside token_required...")
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
            print(f"got token in header")
        if not token:
            print(f"no token found in header")
            return jsonify({'message': 'a valid token is missing'})
        try:
            print(f"decoding token")
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user_uid = data['user_uid']
        except Exception as _e:
            print(traceback.format_exc())
            return jsonify({'message': 'token is invalid'})
        return f(user_uid, *args, **kwargs)
    return decorator


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
        data = {}
        if len(users) == 0:
            # crete new user
            user_uid = random.randint(int(2**60), int(2**64)-1)
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
            data.update({"address": str(user.address), "user_uid": user_uid, 'username': user.username, 'email': user.email})

        # generate jwt
        token = jwt.encode(
            {'user_uid': user_uid, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)},
            app.config['SECRET_KEY'], "HS256")
        data['token'] = token
        return format_response(True, response_code, data)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


########################################################################################################################
########################################################################################################################
# Authenticated Endpoints
@app.route("/update_profile", methods=['POST'])
@token_required
def update_profile(user_uid):
    if user_uid:
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
@token_required
def handle_upload_asset(user_uid):
    try:
        if user_uid:
            image_file = request.files['image']
            file_name = image_file.filename
            file_type = file_name.split(".")[-1]
            image_bytes = request.files['image'].read()
            image_size_bytes = len(image_bytes)

            tmp_fname = f"tmp_{int(time.time())}_{file_name}"
            tmp_fpath = os.path.join('/tmp', tmp_fname)
            with open(tmp_fpath, 'wb') as f:
                f.write(image_bytes)

            file_key = upload_asset(tmp_fpath, tmp_fname)
            os.remove(tmp_fpath)

            _result = tables.Assets.insert(file_path=file_key,
                                           file_type=file_type,
                                           file_name=file_name,
                                           file_size_bytes=image_size_bytes,
                                           creation_timestamp=int(time.time()),
                                           user_uid=user_uid)
            file_path = os.path.join(consts.S3_BASE_URL, file_key)
            asset_data = {'file_path': file_path}
            return format_response(True, ResponseCodes.UPLOAD_SUCCESS.value, data=asset_data)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


@app.route("/update_asset", methods=['POST'])
@token_required
def handle_update_asset(user_uid):
    try:
        if user_uid:
            asset_uid = request.json['asset_uid']
            transaction_signature = request.json['transaction_signature']
            purchase_price = float(request.json['purchase_price'])
            purchase_type = request.json['purchase_type']
            confirmed = int(bool(request.json['confirmed']))
            try:
                confirmation_timestamp = request.json['confirmation_timestamp']
            except KeyError as _e:
                confirmation_timestamp = None
            values = {
                "purchase_type": purchase_type,
                "purchase_price": purchase_price,
                "transaction_signature": transaction_signature,
                "confirmed": confirmed,
            }
            if confirmation_timestamp:
                values['confirmation_timestamp'] = int(confirmation_timestamp)
            _result = tables.Assets.update(values, uid=asset_uid)
            return format_response(True, ResponseCodes.ASSET_UPDATE_SUCCESS.value)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


@app.route("/list_assets", methods=['POST'])
@token_required
def list_assets(user_uid):
    try:
        if user_uid:
            assets = tables.Assets.select(user_uid=user_uid)
            asset_dicts = [x.to_dict() for x in assets]
            return format_response(True, ResponseCodes.LIST_SUCCESS.value, data=asset_dicts)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


@app.route("/download_asset", methods=['POST'])
@token_required
def handle_download_asset(user_uid):
    if user_uid:
        file_key = request.json['file_path']
        tmp_fpath = download_asset(file_key)
        file_type = tmp_fpath.split(".")[-1]
        print(f"got file: {tmp_fpath}, type: {file_type}")
        if file_type.lower() == 'json':
            print(f"returning json")
            data = json.load(open(tmp_fpath))
            return format_response(True, ResponseCodes.DOWNLOAD_JSON_SUCCESS.value, data=data)
        else:
            return send_file(tmp_fpath)
    else:
        return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)




