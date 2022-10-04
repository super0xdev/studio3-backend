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

# sign auth message
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
data = r.json()
token = data['data']['token']
headers = {'x-access-tokens': token}
print(f"using token: {token}")

########################################################################################################################
# TODO all other
# /upload_asset
api_url = os.path.join(url_base, "upload_asset")
print(f"Calling: {api_url}")
asset_fpath = "/home/alphaprime8/PycharmProjects/DsAPI/tmp_upload/meta.json"
files = {'image': open(asset_fpath, 'rb')}
r = session.post(url=api_url, files=files, headers=headers)
print(r.status_code, r.reason, r.text)

# /list_assets
api_url = os.path.join(url_base, "list_assets")
print(f"Calling: {api_url}")
r = session.post(url=api_url, headers=headers)
data = r.json()['data']
file_path = data[0]['file_path']
print(r.status_code, r.reason, r.text)

# /download_asset
data = {'file_path': file_path}
api_url = os.path.join(url_base, "download_asset")
print(f"Calling: {api_url}")
r = session.post(url=api_url, json=data, headers=headers)
print(r.status_code, r.reason)
local_fpath = f"./tmp_download/{file_path}"
with open(local_fpath, 'wb') as f:
    f.write(r.content)
    print(f"Save image to local file: {local_fpath}")

# /update_asset
data = {
    'asset_uid': 11,
    'transaction_signature': "5YBogpMypSw4BJgHcwYjqMxZrtsFsF6Nwa3nUrm92R2o5KPk38r5aN5fThRruAYZ7CkKmQ5BRberRzULSFTPF1FH",
    'purchase_price': 1.1,
    'purchase_type': 'IMAGE_2K_W_WATERMARK',
    'confirmed': 1,
    'confirmation_timestamp': int(time.time())

}
api_url = os.path.join(url_base, "update_asset")
print(f"Calling: {api_url}")
r = session.post(url=api_url, json=data, headers=headers)
print(r.status_code, r.reason, r.text)


