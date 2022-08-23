from solana.keypair import Keypair
import requests
import pickle
import base58
import json
import time
import os
import io

PRODUCTION_MODE = False

if PRODUCTION_MODE:
    url_base = 'https://j0624ut64a.execute-api.us-east-1.amazonaws.com/'
else:
    url_base = 'http://localhost:5000/'

# load test keypair
secrey_key_hex = pickle.load(open('./tmp_creds/secret_key_hex_str.p', 'rb'))
secret_key = bytes.fromhex(secrey_key_hex)
keypair = Keypair.from_secret_key(secret_key)

# sign login message
timestamp = int(time.time())
pubkey = str(keypair.public_key)
msg = bytes(str(timestamp), 'utf8')
signed = keypair.sign(msg)
signatureb58 = base58.b58encode(bytes(signed))
signatureb58_decoded = signatureb58.decode()

# create persistent session
session = requests.Session()

# test register
data = {'address': pubkey, 'timestamp':timestamp, 'signature':signatureb58_decoded}
api_url = os.path.join(url_base, "login")
r = session.post(url=api_url, json=data)
print(r.status_code, r.reason, r.text)

# upload asset
api_url = os.path.join(url_base, "upload_asset")
metadata = {'file_type': 'jpg', 'file_name': 'myavatar666'}
metadata_file = io.StringIO(json.dumps(metadata))
files = {'image': open('/home/myware/PycharmProjects/DstudioApi/tmp_upload/mHYQPS37_400x400.jpg', 'rb'), 'metadata': metadata_file}
r = session.post(url=api_url, files=files)
print(r.status_code, r.reason, r.text)





