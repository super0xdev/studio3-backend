from solana.keypair import Keypair
import requests
import base58
import pickle
import time
import os


PRODUCTION_MODE = False

if PRODUCTION_MODE:
    url_base = 'https://j0624ut64a.execute-api.us-east-1.amazonaws.com/'
else:
    url_base = 'http://127.0.0.1:5000/'

# load keypair
keypair = Keypair.generate()

# sign timestamp to authenticate
timestamp = int(time.time())
pubkey = str(keypair.public_key)
msg = bytes(str(timestamp), 'utf8')
signed = keypair.sign(msg)

signatureb58 = base58.b58encode(bytes(signed))
signatureb58_decoded = signatureb58.decode()

# create persistent session
session = requests.Session()

# /login
data = {'address': pubkey, 'timestamp':timestamp, 'signature':signatureb58_decoded}
api_url = os.path.join(url_base, "login")
print(f"Calling: {api_url}")
r = session.post(url=api_url, json=data)
print(r.status_code, r.reason, r.text)

# TODO add cookie header

# /update_profile
data = {'username': "AlphaPrime88888888", "email": "alphaprime88888888@gmail.com"}
api_url = os.path.join(url_base, "update_profile")
print(f"Calling: {api_url}")
r = session.post(url=api_url, json=data)
print(r.status_code, r.reason, r.text)



