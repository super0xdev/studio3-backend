from flask import Flask, jsonify, make_response, request, redirect
from solana.keypair import Keypair
from solana_utils.verify_signature import verify_address_ownership
import traceback
import logging
import tables
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
        # # TODO check if exists
        # users = tables.Users.select(address=address)
        # if len(users) == 0:
        #     # TODO if not exists, insert
        #     result = tables.Users.insert(address=address,
        #                                  creation_timestamp=int(time.time()),
        #                                  updated_timestamp=int(time.time()))
        # else:
        #     # TODO if exists, return profile
        #     pass
    except Exception as e:
        logging.error(traceback.format_exc())
        # TODO return error code
    return jsonify(message='Hello from root!')


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

