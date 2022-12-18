from solana.keypair import Keypair
import requests
import pickle
import base58
import time
import os
import random

PRODUCTION_MODE = True

if PRODUCTION_MODE:
    # url_base = 'https://j0624ut64a.execute-api.us-east-1.amazonaws.com/'
    # url_base = 'http://studio3loadbalancer-1478688032.us-east-2.elb.amazonaws.com/'
    # url_base = 'https://api.studio3-dev.com/'
    # url_base = 'https://prod.studio3-dev.com/'
    url_base = 'https://dev.studio3-dev.com/'
else:
    url_base = 'http://localhost:5000/'

# load test keypair
USE_NEW = False
if USE_NEW:
    keypair = Keypair.generate()
else:
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

# /upload_asset
api_url = os.path.join(url_base, "upload_asset")
print(f"Calling: {api_url}")
asset_fpath = "/home/alphaprime8/PycharmProjects/DsAPI/tmp_upload/image_thumbnail.png"
files = {'image': open(asset_fpath, 'rb')}
r = session.post(url=api_url, files=files, headers=headers)
print(r.status_code, r.reason, r.text)

# /upload_multi_asset
api_url = os.path.join(url_base, "upload_multi_asset")
print(f"Calling: {api_url}")
asset_fpath = "/home/alphaprime8/PycharmProjects/DsAPI/tmp_upload/image_thumbnail.png"
meta_fpath = "/home/alphaprime8/PycharmProjects/DsAPI/tmp_upload/test_meta.json"
files = {
    'image': open(asset_fpath, 'rb'),
    'meta': open(meta_fpath, 'rb'),
}
r = session.post(url=api_url, files=files, headers=headers)
print(r.status_code, r.reason, r.text)

# /list_assets
api_url = os.path.join(url_base, "list_assets")
print(f"Calling: {api_url}")
r = session.post(url=api_url, headers=headers)
data = r.json()['data']
file_path = data[-1]['file_path']
asset_uid = data[-1]['uid']
print(r.status_code, r.reason, r.text)

# /list_template_assets
api_url = os.path.join(url_base, "list_template_assets")
print(f"Calling: {api_url}")
r = session.post(url=api_url, headers=headers)
data = r.json()['data']
file_path = data[-1]['file_path']
asset_uid = data[-1]['uid']
print(r.status_code, r.reason, r.text)

# /overwrite_asset
print(f"overwriting {file_path} {asset_uid}")

api_url = os.path.join(url_base, "overwrite_asset")
print(f"Calling: {api_url}")
asset_fpath = "/home/alphaprime8/PycharmProjects/DsAPI/tmp_upload/image_thumbnail.png"
files = {'image': open(asset_fpath, 'rb')}
json_data = {
    "asset_uid": asset_uid,
    "file_key": file_path,
}
r = session.post(url=api_url, files=files, headers=headers, data=json_data)
print(r.status_code, r.reason, r.text)

# TESTS
# /overwrite_multi_asset
print(f"overwriting {file_path} {asset_uid}")

api_url = os.path.join(url_base, "overwrite_multi_asset")
print(f"Calling: {api_url}")
asset_fpath = "/home/alphaprime8/PycharmProjects/DsAPI/tmp_upload/image_thumbnail.png"
meta_fpath = "/home/alphaprime8/PycharmProjects/DsAPI/tmp_upload/test_meta_1.json"
files = {'image': open(asset_fpath, 'rb'), 'meta': open(meta_fpath, 'rb')}
json_data = {
    "asset_uid": asset_uid,
    "file_key": file_path,
}
r = session.post(url=api_url, files=files, headers=headers, data=json_data)
print(r.status_code, r.reason, r.text)

# /duplicate_asset
print(f"duplicating {file_path} {asset_uid}")
api_url = os.path.join(url_base, "duplicate_asset")

print(f"Calling: {api_url}")
json_data = {
    "asset_uid": 139,
}
r = session.post(url=api_url, headers=headers, data=json_data)
print(r.status_code, r.reason, r.text)

############################
# /duplicate_multi_asset
print(f"duplicating {file_path} {asset_uid}")
api_url = os.path.join(url_base, "duplicate_multi_asset")

print(f"Calling: {api_url}")
json_data = {
    "asset_uid": asset_uid,
}
r = session.post(url=api_url, headers=headers, json=json_data)
print(r.status_code, r.reason, r.text)

############################
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
    'asset_uid': asset_uid,
    'transaction_signature': "5ogpMypSw4BJgHcwYjqMxZrtsFsF6Nwa3nUrm92R2o5KPk38r5aN5fThRruAYZ7CkKmQ5BRberRzULSFTPF1FH",
    'purchase_price': 1.1,
    'purchase_type': 'IMAGE_2K_W_WATERMARK',
    'confirmed': 1,
    'confirmation_timestamp': int(time.time()),
    'file_name': "My First Filename..."

}
api_url = os.path.join(url_base, "update_asset_metadata")
print(f"Calling: {api_url}")
r = session.post(url=api_url, json=data, headers=headers)
print(r.status_code, r.reason, r.text)

# /delete_asset
data = {
    'asset_uid': asset_uid,
    'file_key': file_path
}
api_url = os.path.join(url_base, "delete_asset")
print(f"Calling: {api_url}")
r = session.post(url=api_url, json=data, headers=headers)
print(r.status_code, r.reason, r.text)

# /export asset
api_url = os.path.join(url_base, "export_asset")
print(f"Calling: {api_url}")
asset_fpath = "/home/alphaprime8/PycharmProjects/DsAPI/tmp_upload/droid_alpha.png"
files = {'image': open(asset_fpath, 'rb')}
r = session.post(url=api_url, files=files, headers=headers)
print(r.status_code, r.reason)
local_fpath = f"./tmp_download/{int(time.time()*1000)}_{int(random.random()*1000)}.png"
with open(local_fpath, 'wb') as f:
    f.write(r.content)
    print(f"Save image to local file: {local_fpath}")




