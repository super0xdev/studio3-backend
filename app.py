"""
sudo chmod 666 /var/run/docker.sock
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 707000167678.dkr.ecr.us-east-2.amazonaws.com

sudo docker build -t studio3api .
docker tag studio3api:latest 707000167678.dkr.ecr.us-east-2.amazonaws.com/studio3api:latest
docker push 707000167678.dkr.ecr.us-east-2.amazonaws.com/studio3api:latest

"""
from solana_utils.verify_signature import verify_address_ownership
from flask import Flask, jsonify, make_response, request, send_file
from flask_cors import CORS
from response_utils.response_codes import ResponseCodes
import response_utils.exceptions as errs
from response_utils.format_reponse import format_response
import traceback
from image_utils.add_watermark import add_watermark
from image_utils.generate_thumbnail import generate_thumbnail
from s3_utils.upload_asset import upload_asset
from s3_utils.duplicate_asset import duplicate_asset
from s3_utils.download_asset import download_asset
from s3_utils.delete_asset import delete_asset
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
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
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
        print(f"got userse: {users}")
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
            data.update({"address": str(user.address), "user_uid": user_uid,
                        'username': user.username, 'email': user.email})

        # generate jwt
        token = jwt.encode(
            {'user_uid': user_uid, 'exp': datetime.datetime.utcnow() +
             datetime.timedelta(minutes=45)},
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


########################################################################################################################
########################################################################################################################
########################################################################################################################
@app.route("/upload_multi_asset", methods=['POST'])
@token_required
def handle_upload_multi_asset(user_uid):
    try:
        if user_uid:

            # parse and upload image file
            image_file = request.files['image']
            image_file_name = image_file.filename
            image_file_type = image_file_name.split(".")[-1]
            image_bytes = request.files['image'].read()
            image_size_bytes = len(image_bytes)
            if image_size_bytes > consts.MAX_FILE_SIZE_BYTES:
                raise errs.MaxFileSizeExceeded()
            tmp_fname = f"tmp_{int(time.time())}_{image_file_name}"
            tmp_fpath = os.path.join('/tmp', tmp_fname)
            thumbnail_fpath = os.path.join('/tmp', "thumbnail_"+tmp_fname)
            with open(tmp_fpath, 'wb') as f:
                f.write(image_bytes)
            image_file_key = upload_asset(tmp_fpath, tmp_fname)
            generate_thumbnail(tmp_fpath, thumbnail_fpath)
            thumbnail_file_key = upload_asset(
                thumbnail_fpath, "thumbnail_"+tmp_fname)
            os.remove(tmp_fpath)
            os.remove(thumbnail_fpath)

            ###################################################################
            # parse and upload meta file

            meta_file = request.files['meta']
            meta_file_name = meta_file.filename
            # meta_file_type = meta_file_name.split(".")[-1]
            meta_bytes = request.files['meta'].read()
            meta_size_bytes = len(meta_bytes)
            if meta_size_bytes > consts.MAX_FILE_SIZE_BYTES:
                raise errs.MaxFileSizeExceeded()
            tmp_fname = f"tmp_{int(time.time())}_{meta_file_name}"
            tmp_fpath = os.path.join('/tmp', tmp_fname)
            with open(tmp_fpath, 'wb') as f:
                f.write(meta_bytes)
            meta_file_key = upload_asset(tmp_fpath, tmp_fname)
            os.remove(tmp_fpath)

            _result = tables.Assets.insert(
                file_path=image_file_key,
                thumbnail_file_path=thumbnail_file_key,
                file_type=image_file_type,
                file_name=image_file_name,
                file_size_bytes=image_size_bytes,
                meta_file_path=meta_file_key,
                creation_timestamp=int(time.time()),
                user_uid=user_uid)

            image_file_path = os.path.join(consts.S3_BASE_URL, image_file_key)
            thumbnail_file_path = os.path.join(
                consts.S3_BASE_URL, thumbnail_file_key)
            meta_file_path = os.path.join(consts.S3_BASE_URL, meta_file_key)

            asset_data = {'image_file_path': image_file_path,
                          "thumbnail_file_path": thumbnail_file_path,
                          'meta_file_path': meta_file_path}
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


########################################################################################################################
########################################################################################################################
########################################################################################################################

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
            if image_size_bytes > consts.MAX_FILE_SIZE_BYTES:
                raise errs.MaxFileSizeExceeded()
            tmp_fname = f"tmp_{int(time.time())}_{file_name}"
            tmp_fpath = os.path.join('/tmp', tmp_fname)
            thumbnail_fpath = os.path.join('/tmp', "thumbnail_"+tmp_fname)
            with open(tmp_fpath, 'wb') as f:
                f.write(image_bytes)
            file_key = upload_asset(tmp_fpath, tmp_fname)
            generate_thumbnail(tmp_fpath, thumbnail_fpath)
            thumbnail_file_key = upload_asset(
                thumbnail_fpath, "thumbnail_"+tmp_fname)
            os.remove(tmp_fpath)
            os.remove(thumbnail_fpath)
            tab = request.form['tab']
            collection = request.form['collection']
            tags = request.form['tags']
            _result = tables.Assets.insert(file_path=file_key,
                                           thumbnail_file_path=thumbnail_file_key,
                                           file_type=file_type,
                                           file_name=file_name,
                                           file_size_bytes=image_size_bytes,
                                           creation_timestamp=int(time.time()),
                                           user_uid=user_uid,
                                           tab=tab,
                                           collection=collection,
                                           tags=tags)
            file_path = os.path.join(consts.S3_BASE_URL, file_key)
            thumbnail_file_path = os.path.join(
                consts.S3_BASE_URL, thumbnail_file_key)
            asset_data = {'file_path': file_path,
                          "thumbnail_file_path": thumbnail_file_path}
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

########################################################################################################################
########################################################################################################################
########################################################################################################################


@app.route("/upload_template_asset", methods=['POST'])
@token_required
def handle_upload_template_asset(user_uid):
    try:
        if user_uid:
            uploaded_files = request.files.getlist('image')
            file_path = ''
            thumbnail_file_path = ''
            address = request.form['address']
            for file in uploaded_files:
                image_file = file
                file_name = image_file.filename
                file_type = file_name.split(".")[-1]
                image_bytes = file.read()
                image_size_bytes = len(image_bytes)
                if image_size_bytes > consts.MAX_FILE_SIZE_BYTES:
                    raise errs.MaxFileSizeExceeded()
                tmp_fname = f"tmp_{int(time.time())}_{file_name}"
                tmp_fpath = os.path.join('/tmp', tmp_fname)
                thumbnail_fpath = os.path.join('/tmp', "thumbnail_"+tmp_fname)
                with open(tmp_fpath, 'wb') as f:
                    f.write(image_bytes)
                file_key = upload_asset(tmp_fpath, tmp_fname)
                generate_thumbnail(tmp_fpath, thumbnail_fpath)
                thumbnail_file_key = upload_asset(
                    thumbnail_fpath, "thumbnail_"+tmp_fname)
                os.remove(tmp_fpath)
                os.remove(thumbnail_fpath)
                tab = request.form['tab']
                collection = request.form['collection']
                tags = request.form['tags']
                if (tab == ''):
                    tab = 'NULL'
                if (collection == ''):
                    collection = 'NULL'
                if (tags == ''):
                    tags = 'NULL'
                _result = tables.Assets.insert(file_path=file_key,
                                            thumbnail_file_path=thumbnail_file_key,
                                            file_type=file_type,
                                            file_name=file_name,
                                            file_size_bytes=image_size_bytes,
                                            creation_timestamp=int(time.time()),
                                            user_uid=consts.ADMIN_USER_UID,
                                            tab=tab,
                                            collection=collection,
                                            tags=tags,
                                            owner=address
                                            )
            asset_data = {'file_path': file_path,
                "thumbnail_file_path": thumbnail_file_path}
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



#######################################################################################################################
@app.route("/overwrite_multi_asset", methods=['POST'])
@token_required
def handle_overwrite_multi_asset(user_uid):
    try:
        if user_uid:

            logging.info(f"inside overwrite")

            # extract existing file params
            asset_uid = request.form['asset_uid']
            file_key = request.form['file_key']

            logging.info(f"got asset_uid: {asset_uid}, file_key: {file_key}")

            # lookup thumbnail file key
            source_asset: tables.Assets = tables.Assets.select(uid=asset_uid)[
                0]

            # extract image data
            image_file = request.files['image']
            file_name = image_file.filename
            image_bytes = request.files['image'].read()
            image_size_bytes = len(image_bytes)

            logging.info(f"got image file: {file_name}, {image_bytes} bytes")

            if image_size_bytes > consts.MAX_FILE_SIZE_BYTES:
                raise errs.MaxFileSizeExceeded()

            # save tmp
            tmp_fname = f"tmp_{int(random.random()*1000)}_{int(time.time())}_{file_name}"
            # TODO maybe error
            logging.info(f"got 1")
            thumbnail_fpath = os.path.join('/tmp', "thumbnail_"+tmp_fname)
            # TODO maybe error
            tmp_fpath = os.path.join('/tmp', tmp_fname)
            logging.info(f"got 2")
            with open(tmp_fpath, 'wb') as f:
                f.write(image_bytes)

            logging.info(f"saved image")

            # generate thumbnail
            try:
                generate_thumbnail(tmp_fpath, thumbnail_fpath)
                _ = upload_asset(
                    thumbnail_fpath, source_asset.thumbnail_file_path, overwrite=True)
            except Exception as e:
                logging.error(f"exception on thumbnail: {e}")
                logging.info(traceback.format_exc())
                logging.info("failed to update thumbnail...")

            logging.info(f"overwriting image and thumbnail")

            # upload to s3 and cleanup
            _ = upload_asset(tmp_fpath, file_key, overwrite=True)
            os.remove(tmp_fpath)

            logging.info(f"overwrite complete")

            # upload meta
            ###############################
            meta_file = request.files['meta']
            meta_file_name = meta_file.filename

            logging.info(f"got meta_file_name: {meta_file_name}")

            # meta_file_type = meta_file_name.split(".")[-1]
            meta_bytes = request.files['meta'].read()
            meta_size_bytes = len(meta_bytes)

            logging.info(f"got meta bytes: {meta_size_bytes}")

            if meta_size_bytes > consts.MAX_FILE_SIZE_BYTES:
                raise errs.MaxFileSizeExceeded()
            tmp_fname = f"tmp_{int(time.time())}_{meta_file_name}_{int(random.random()*1000)}"
            # TODO maybe error
            tmp_fpath = os.path.join('/tmp', tmp_fname)
            logging.info(f"got 3")
            logging.info(f"writing meta")
            with open(tmp_fpath, 'wb') as f:
                f.write(meta_bytes)
            meta_file_key = upload_asset(tmp_fpath, tmp_fname)
            logging.info(f"uploaded meta with key: {meta_file_key}")
            os.remove(tmp_fpath)

            ###############################

            # update asset metadata
            values = {
                "file_size_bytes": image_size_bytes,
                "update_timestamp": int(time.time()),
                "meta_file_path": meta_file_key,
            }
            _result = tables.Assets.update(values,
                                           uid=asset_uid,
                                           file_path=file_key,
                                           user_uid=user_uid)
            assert _result == 1, "No asset was updated in database."
            # TODO maybe error
            file_path = os.path.join(consts.S3_BASE_URL, file_key)
            logging.info(f"got 4")
            # TODO maybe error
            try:
                thumbnail_file_path = os.path.join(
                    consts.S3_BASE_URL, source_asset.thumbnail_file_path)
                logging.info(f"got 5")
            except:
                logging.info("got no thumbnail file path")
                thumbnail_file_path = ""
            # TODO maybe error
            meta_file_path = os.path.join(consts.S3_BASE_URL, meta_file_key)
            logging.info(f"got 6")

            asset_data = {'file_path': file_path,
                          "thumbnail_file_path": thumbnail_file_path, "meta_file_path": meta_file_path}

            return format_response(True, ResponseCodes.OVERWRITE_SUCCESS.value, data=asset_data)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        logging.info(f"TOP LEVEL OVERWRITE ERROR")
        logging.info(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


#######################################################################################################################


@app.route("/overwrite_asset", methods=['POST'])
@token_required
def handle_overwrite_asset(user_uid):
    try:
        if user_uid:

            # extract existing file params
            asset_uid = request.form['asset_uid']
            file_key = request.form['file_key']

            # lookup thumbnail file key
            source_asset: tables.Assets = tables.Assets.select(uid=asset_uid)[
                0]

            # extract image data
            image_file = request.files['image']
            file_name = image_file.filename
            image_bytes = request.files['image'].read()
            image_size_bytes = len(image_bytes)

            if image_size_bytes > consts.MAX_FILE_SIZE_BYTES:
                raise errs.MaxFileSizeExceeded()

            # save tmp
            tmp_fname = f"tmp_{int(time.time())}_{file_name}"
            thumbnail_fpath = os.path.join('/tmp', "thumbnail_"+tmp_fname)
            tmp_fpath = os.path.join('/tmp', tmp_fname)
            with open(tmp_fpath, 'wb') as f:
                f.write(image_bytes)

            # generate thumbnail
            generate_thumbnail(tmp_fpath, thumbnail_fpath)

            # upload to s3 and cleanup
            _ = upload_asset(tmp_fpath, file_key, overwrite=True)
            _ = upload_asset(
                thumbnail_fpath, source_asset.thumbnail_file_path, overwrite=True)
            os.remove(tmp_fpath)

            # update asset metadata
            values = {
                "file_size_bytes": image_size_bytes,
                "update_timestamp": int(time.time()),
            }
            _result = tables.Assets.update(values,
                                           uid=asset_uid,
                                           file_path=file_key,
                                           user_uid=user_uid)
            assert _result == 1, "No asset was updated in database."
            file_path = os.path.join(consts.S3_BASE_URL, file_key)
            thumbnail_file_path = os.path.join(
                consts.S3_BASE_URL, source_asset.thumbnail_file_path)
            asset_data = {'file_path': file_path,
                          "thumbnail_file_path": thumbnail_file_path}
            return format_response(True, ResponseCodes.OVERWRITE_SUCCESS.value, data=asset_data)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


@app.route("/duplicate_asset", methods=['POST'])
@token_required
def handle_duplicate_asset(user_uid):
    try:
        if user_uid:
            print(f"P: requestion duplicate asset: {request.json}")
            logging.info(f"L: requestion duplicate asset: {request.json}")
            asset_uid = request.json['asset_uid']
            print(f"P: duplicatin assing uid: {asset_uid}")
            logging.info(f"L: duplicatin assing uid: {asset_uid}")
            source_asset: tables.Assets = tables.Assets.select(uid=asset_uid)[
                0]
            print(f"P: got source aset: {source_asset.file_path}")
            logging.info(f"L: got source aset: {source_asset.file_path}")
            new_file_key = duplicate_asset(
                source_asset.file_path, source_asset.file_name)
            logging.info(f"inserting duplicated file")
            print(f"inserting duplicated file")
            _result = tables.Assets.insert(file_path=new_file_key,
                                           file_type=source_asset.file_type,
                                           file_name=source_asset.file_name,
                                           file_size_bytes=source_asset.file_size_bytes,
                                           creation_timestamp=int(time.time()),
                                           user_uid=user_uid)
            logging.info(f"inserted duplicated file: {new_file_key}")
            print(f"inserted duplicated file: {new_file_key}")
            file_path = os.path.join(consts.S3_BASE_URL, new_file_key)
            asset_data = {'file_path': file_path}
            return format_response(True, ResponseCodes.DUPLICATE_SUCCESS.value, data=asset_data)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


@app.route("/update_asset_metadata", methods=['POST'])
@token_required
def handle_update_asset_metadata(user_uid):
    try:
        if user_uid:
            asset_uid = request.json['asset_uid']
            file_name = request.json['file_name']
            transaction_signature = request.json['transaction_signature']
            purchase_price = float(request.json['purchase_price'])
            purchase_type = request.json['purchase_type']
            confirmed = int(bool(request.json['confirmed']))
            try:
                confirmation_timestamp = request.json['confirmation_timestamp']
            except KeyError as _e:
                confirmation_timestamp = None
            values = {
                "file_name": file_name,
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


########################################################################################################################
########################################################################################################################
########################################################################################################################
@app.route("/duplicate_multi_asset", methods=['POST'])
@token_required
def handle_duplicate_multi_asset(user_uid):
    try:
        if user_uid:
            asset_uid = request.json['asset_uid']

            source_asset: tables.Assets = tables.Assets.select(uid=asset_uid)[
                0]

            new_file_key = duplicate_asset(
                source_asset.file_path, source_asset.file_name)
            # meta_file_key = duplicate_asset(
            #     source_asset.meta_file_path, f"meta_{source_asset.file_name}")

            _result = tables.Assets.insert(file_path=new_file_key,
                                           file_type=source_asset.file_type,
                                           file_name=source_asset.file_name,
                                           file_size_bytes=source_asset.file_size_bytes,
                                           creation_timestamp=int(time.time()),
                                           thumbnail_file_path=source_asset.thumbnail_file_path,
                                           # meta_file_path=meta_file_key,
                                           user_uid=user_uid)

            logging.info(f"inserted duplicated file: {new_file_key}")
            print(f"inserted duplicated file: {new_file_key}")
            file_path = os.path.join(consts.S3_BASE_URL, new_file_key)
            asset_data = {'file_path': file_path}
            return format_response(True, ResponseCodes.DUPLICATE_SUCCESS.value, data=asset_data)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


########################################################################################################################
########################################################################################################################
########################################################################################################################
@app.route("/delete_asset", methods=['POST'])
@token_required
def handle_delete_asset(user_uid):
    try:
        if user_uid:
            asset_uid = request.json['asset_uid']
            file_key = request.json['file_key']
            file_name = request.json['file_name']
            items = tables.Assets.select(file_name=file_name)
            for item in items:
                tables.Assets.delete(uid=item.uid)
                delete_asset(item.file_path)
            return format_response(True, ResponseCodes.DELETE_ASSET_SUCCESS.value)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


@app.route("/delete_user_asset", methods=['POST'])
@token_required
def handle_delete_user_asset(user_uid):
    try:
        if user_uid:
            asset_uid = request.json['asset_uid']
            file_key = request.json['file_key']
            tables.Assets.delete(uid = asset_uid)
            delete_asset(file_key)
            return format_response(True, ResponseCodes.DELETE_ASSET_SUCCESS.value)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


@app.route("/get_categories", methods=['POST'])
@token_required
def get_categories(user_uid):
    try:
        if user_uid:
            assets = tables.Assets.select(user_uid=consts.ADMIN_USER_UID)
            asset_dicts = [x.to_dict() for x in assets]
            res_data = {
                'tab': [],
                'collection': [],
                'tags': []
            }
            for data in asset_dicts:
                if (data['tab'] != None):
                    res_data['tab'].append(data['tab'])
                if (data['collection'] != None):
                    res_data['collection'].append(data['collection'])
                if (data['tags'] != None):
                    res_data['tags'].append(data['tags'])
            res_data = {
                'tab': list(set(res_data['tab'])),
                'collection': list(set(res_data['collection'])),
                'tags': list(set(res_data['tags']))
            }
            return format_response(True, ResponseCodes.LIST_SUCCESS.value, data=res_data)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)

@app.route("/list_tags", methods=['POST'])
@token_required
def list_tags(user_uid):
    try:
        if user_uid:
            tags = tables.Tags.select()
            tag_dicts = [x.to_dict() for x in tags]
            return format_response(True, ResponseCodes.LIST_SUCCESS.value, data=tag_dicts)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)

@app.route("/insert_tag", methods=['POST'])
@token_required
def insert_tag(user_uid):
    try:
        if user_uid:
            tid = request.form['id']
            ttag = request.form['tag']
            
            tables.Tags.insert(id=tid, tag=ttag)

            return format_response(True, ResponseCodes.DUPLICATE_SUCCESS.value, data="success")
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


@app.route("/list_template_assets", methods=['POST'])
@token_required
def list_template_assets(user_uid):
    try:
        if user_uid:
            assets = tables.Assets.select(user_uid=consts.ADMIN_USER_UID)
            asset_dicts = [x.to_dict() for x in assets]
            return format_response(True, ResponseCodes.LIST_TEMPLATES_SUCCESS.value, data=asset_dicts)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


@app.route("/list_template_assets_by_category", methods=['POST'])
@token_required
def list_template_assets_by_category(user_uid):
    try:
        if user_uid:
            tab = request.form['tab']
            collection = request.form['collection']
            tags = request.form['tags']
            if (tab == ''):
                if (collection == ''):
                    if (tags == ''):
                        assets = tables.Assets.select(
                            user_uid=consts.ADMIN_USER_UID)
                    else:
                        assets = tables.Assets.select(
                            user_uid=consts.ADMIN_USER_UID, tags=tags)
                else:
                    if (tags == ''):
                        assets = tables.Assets.select(
                            user_uid=consts.ADMIN_USER_UID, collection=collection)
                    else:
                        assets = tables.Assets.select(
                            user_uid=consts.ADMIN_USER_UID, collection=collection, tags=tags)
            else:
                if (collection == ''):
                    if (tags == ''):
                        assets = tables.Assets.select(
                            user_uid=consts.ADMIN_USER_UID, tab=tab)
                    else:
                        assets = tables.Assets.select(
                            user_uid=consts.ADMIN_USER_UID, tab=tab, tags=tags)
                else:
                    if (tags == ''):
                        assets = tables.Assets.select(
                            user_uid=consts.ADMIN_USER_UID, tab=tab, collection=collection)
                    else:
                        assets = tables.Assets.select(
                            user_uid=consts.ADMIN_USER_UID, tab=tab, collection=collection, tags=tags)
            asset_dicts = [x.to_dict() for x in assets]
            return format_response(True, ResponseCodes.LIST_TEMPLATES_SUCCESS.value, data=asset_dicts)
        else:
            return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)
    except Exception as e:
        print(traceback.format_exc())
        if hasattr(e, "code"):
            response_code = e.code
        else:
            response_code = str(e)
        return format_response(False, response_code)


########################################################################################################################
########################################################################################################################
########################################################################################################################
@app.route("/export_asset", methods=['POST'])
@token_required
def handle_export_asset(user_uid):
    if user_uid:
        image_file = request.files['image']
        image_file_name = image_file.filename
        image_bytes = request.files['image'].read()
        image_size_bytes = len(image_bytes)
        if image_size_bytes > consts.MAX_FILE_SIZE_BYTES:
            raise errs.MaxFileSizeExceeded()
        tmp_fname = f"tmp_{int(time.time())}_{image_file_name}"
        # TODO consider useing jpeg
        tmp_fpath = os.path.join('/tmp', tmp_fname)
        with open(tmp_fpath, 'wb') as f:
            f.write(image_bytes)
        export_fpath = add_watermark(tmp_fpath)
        return send_file(export_fpath)
    else:
        return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)


########################################################################################################################
########################################################################################################################
########################################################################################################################
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
            add_watermark(tmp_fpath)
            return send_file(tmp_fpath)
    else:
        return format_response(False, ResponseCodes.NOT_LOGGED_IN.value)


@app.route('/')
def home():
    return format_response(True, "Hello World")


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)


if __name__ == "__main__":
    # app.run(threaded=True, host="0.0.0.0", port=8081)
    app.run(threaded=True, host="0.0.0.0", port=80)
