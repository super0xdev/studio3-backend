import boto3
from dotenv import load_dotenv
import os
import uuid
import logging
import time
load_dotenv()

# bucket_name = "d3-studio-assets-1660843754077"
bucket_name = os.environ.get("bucket_name")

def rand_prefix():
    return str(uuid.uuid4().hex[:6])


def duplicate_asset(source_file_key, filename):
    aws_access_key_id = os.environ.get("s3_aws_access_key_id")
    aws_secret_access_key = os.environ.get("s3_aws_secret_access_key")
    s3_resource = boto3.resource("s3",
                                 region_name="us-west-1",
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key)
    bucket = s3_resource.Bucket(bucket_name)
    copy_source = {
        'Bucket': bucket_name,
        'Key': source_file_key
    }
    new_file_key = rand_prefix() + "_" + str(int(time.time()*1000)) + "_" + filename
    copy_response = bucket.copy(copy_source, new_file_key, ExtraArgs={'ACL': "public-read"})
    logging.info(f"Uploaded to S3 with response: {copy_response}")
    return new_file_key
