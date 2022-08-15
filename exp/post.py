from solana.keypair import Keypair
import requests
import base58
import time

# sign
keypair = Keypair.generate()
timestamp = int(time.time())
pubkey = str(keypair.public_key)
msg = bytes(str(timestamp), 'utf8')
signed = keypair.sign(msg)
signatureb58 = base58.b58encode(bytes(signed))
signatureb58_decoded = signatureb58.decode()

# pack
data = {'address': pubkey, 'timestamp':timestamp, 'signature':signatureb58_decoded}

# send
api_url = 'http://localhost:5000/login'
r = requests.post(url=api_url, json=data)
print(r.status_code, r.reason, r.text)


