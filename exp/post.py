import requests
import json
import os
import io

PRODUCTION_MODE = False

if PRODUCTION_MODE:
    base_url = 'https://j0624ut64a.execute-api.us-east-1.amazonaws.com/'
else:
    base_url = 'http://localhost:5000/'


api_url = os.path.join(base_url, "upload_asset")
pubkey = "Ba5ZQRTAGbgTdRLjgtvsNwipRMW2yhidWTQ9jDqJePim"
metadata = {'address': pubkey}
metadata_file = io.StringIO(json.dumps(metadata))
files = {'image': open('/home/myware/PycharmProjects/DstudioApi/tmp_upload/mHYQPS37_400x400.jpg', 'rb'), 'metadata': metadata_file}
r = requests.post(url=api_url, files=files)
print(r.status_code, r.reason, r.text)


# # TODO
# s = requests.Session()
# s.post('https://localhost/login.py', login_data)
# # logged in! cookies saved for future requests.
# r2 = s.get('https://localhost/profile_data.json', ...)
# # cookies sent automatically!
# # do whatever, s will keep your cookies intact :)