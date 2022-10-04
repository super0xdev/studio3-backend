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
# secrey_key_hex = pickle.load(open('./tmp_creds/secret_key_hex_str.p', 'rb'))
# secret_key = bytes.fromhex(secrey_key_hex)
# keypair = Keypair.from_secret_key(secret_key)

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

# /update_profile
data = {'username': "AlphaPrime88888888", "email": "alphaprime88888888@gmail.com"}
api_url = os.path.join(url_base, "update_profile")
print(f"Calling: {api_url}")
r = session.post(url=api_url, json=data)
print(r.status_code, r.reason, r.text)

# /upload_asset
api_url = os.path.join(url_base, "upload_asset")
print(f"Calling: {api_url}")
asset_fpath = "/home/alphaprime8/PycharmProjects/DsAPI/tmp_upload/meta.json"
files = {'image': open(asset_fpath, 'rb')}
r = session.post(url=api_url, files=files)
print(r.status_code, r.reason, r.text)

# /list_assets
api_url = os.path.join(url_base, "list_assets")
print(f"Calling: {api_url}")
r = session.post(url=api_url)
data = r.json()['data']
file_path = data[0]['file_path']
print(r.status_code, r.reason, r.text)

# /download_asset
data = {'file_path': file_path}
api_url = os.path.join(url_base, "download_asset")
print(f"Calling: {api_url}")
r = session.post(url=api_url, json=data)
print(r.status_code, r.reason)
local_fpath = f"./tmp_download/{file_path}"
with open(local_fpath, 'wb') as f:
    f.write(r.content)
    print(f"Save image to local file: {local_fpath}")

# /update_asset

"""
_user_uid = session['user_uid']
asset_uid = request.json['asset_uid']
transaction_signature = request.json['transaction_signature']
purchase_price = float(request.json['purchase_price'])
purchase_type = request.json['purchase_type']
confirmed = int(bool(request.json['confirmed']))
confirmation_timestamp = request.json['confirmation_timestamp']
"""
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
r = session.post(url=api_url, json=data)
print(r.status_code, r.reason, r.text)


