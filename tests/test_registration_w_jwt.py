from solana.keypair import Keypair
import requests
import pickle
import base58
import time
import os

PRODUCTION_MODE = True

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
data = r.json()
token = data['data']['token']
print(f"using token: {token}")


# /update_profile
data = {'username': "AlphaPrimexx8888898878", "email": "alphaprimexx8388889888@gmail.com"}
headers = {'x-access-tokens': token}
api_url = os.path.join(url_base, "update_profile")
print(f"Calling: {api_url}")
r = session.post(url=api_url, json=data, headers=headers)
print(r.status_code, r.reason, r.text)

# save creds locally
secret_key_hex_str = keypair.secret_key.hex()
pickle.dump(secret_key_hex_str, open('./tmp_creds/secret_key_hex_str.p', 'wb'))
print(f"dumped secret key to tmp file")


