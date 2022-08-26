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
    url_base = 'http://localhost:5000/'

# load keypair
secrey_key_hex = pickle.load(open('./tmp_creds/secret_key_hex_str.p', 'rb'))
secret_key = bytes.fromhex(secrey_key_hex)
keypair = Keypair.from_secret_key(secret_key)

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
data = {'username': "AlphaPrime888888", "email": "alphaprime888888@gmail.com"}
api_url = os.path.join(url_base, "update_profile")
print(f"Calling: {api_url}")
r = session.post(url=api_url, json=data)
print(r.status_code, r.reason, r.text)

# /upload_asset
api_url = os.path.join(url_base, "upload_asset")
print(f"Calling: {api_url}")
asset_fpath = "/home/myware/PycharmProjects/DstudioApi/tmp_upload/ape1.png"
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


