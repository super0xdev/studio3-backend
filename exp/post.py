from solana.keypair import Keypair
import requests
import base58
import time

# sign
keypair = Keypair.generate()
slot = int(time.time())
pubkey = str(keypair.public_key)
msg = bytes(str(slot), 'utf8')
signed = keypair.sign(msg)
signatureb58 = base58.b58encode(bytes(signed))
signatureb58_decoded = signatureb58.decode()

# sig_encoded = signatureb58_decoded.encode()
# signatureb58 = base58.b58encode(signature)

# pack
create_row_data = {'address': pubkey, 'timestamp':slot, 'signature':signatureb58_decoded}

# send
api_url = 'http://localhost:5000/login'
r = requests.post(url=api_url, json=create_row_data)
print(r.status_code, r.reason, r.text)


