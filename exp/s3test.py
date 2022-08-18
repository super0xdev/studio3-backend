import boto3
from dotenv import load_dotenv
import os
import uuid
load_dotenv()

first = False
public = True

# init
aws_access_key_id = os.environ.get("s3_aws_access_key_id")
aws_secret_access_key = os.environ.get("s3_aws_secret_access_key")
s3_resource = boto3.resource("s3",
                             region_name="us-west-1",
                             aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key)

# create bucket
bucket_name = "d3-studio-assets-1660843754077"
if first:
    bucket = s3_resource.create_bucket(Bucket=bucket_name,
                                         CreateBucketConfiguration={
                                             'LocationConstraint': 'us-west-1'
                                         })
else:
    bucket = s3_resource.Bucket(bucket_name)


# upload file
def rand_prefix():
    return str(uuid.uuid4().hex[:6])

fpath = "/home/myware/PycharmProjects/DstudioApi/tmp_upload/mHYQPS37_400x400.jpg"
file_key_private = "3c032fmy_avatar_0.png"
file_key_public = "mHYQPS37_400x400.jpg"

if not public:
    upload_response = bucket.upload_file(Filename=fpath, Key=file_key_private)
else:
    upload_response = bucket.upload_file(Filename=fpath, Key=file_key_public, ExtraArgs={'ACL': "public-read"})



# download file
download_response = s3_resource.Object(bucket_name, file_key_private).download_file(
    f'/home/myware/PycharmProjects/DstudioApi/tmp_download/{file_key_private}')

