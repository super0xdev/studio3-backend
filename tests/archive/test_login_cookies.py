from solana.keypair import Keypair
import requests
import base58
import time
import os

PRODUCTION_MODE = False

if PRODUCTION_MODE:
    url_base = 'https://j0624ut64a.execute-api.us-east-1.amazonaws.com/'
else:
    url_base = 'http://localhost:5000/'

# sign
keypair = Keypair.generate()
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

# update profile
data = {'username': "AlphaPrime8", "email": "alphaprime8@gmail.com"}
api_url = os.path.join(url_base, "update_profile")
r = session.post(url=api_url, json=data)
print(r.status_code, r.reason, r.text)

