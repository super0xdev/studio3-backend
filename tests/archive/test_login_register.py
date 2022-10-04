from solana.keypair import Keypair
import requests
import base58
import time

PRODUCTION_MODE = True

if PRODUCTION_MODE:
    api_url = 'https://j0624ut64a.execute-api.us-east-1.amazonaws.com/login'
else:
    api_url = 'http://localhost:5000/login'

# sign
keypair = Keypair.generate()
timestamp = int(time.time())
pubkey = str(keypair.public_key)
msg = bytes(str(timestamp), 'utf8')
signed = keypair.sign(msg)
signatureb58 = base58.b58encode(bytes(signed))
signatureb58_decoded = signatureb58.decode()

# test register
data = {'address': pubkey, 'timestamp':timestamp, 'signature':signatureb58_decoded}
r = requests.post(url=api_url, json=data)
print(r.status_code, r.reason, r.text)

# test login
data = {'address': pubkey, 'timestamp':timestamp, 'signature':signatureb58_decoded}
r = requests.post(url=api_url, json=data)
print(r.status_code, r.reason, r.text)

# test signature
data = {'address': pubkey, 'timestamp':0, 'signature':signatureb58_decoded}
r = requests.post(url=api_url, json=data)
print(r.status_code, r.reason, r.text)
