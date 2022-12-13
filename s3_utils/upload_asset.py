import boto3
from dotenv import load_dotenv
import os
import uuid
load_dotenv()
import logging

# bucket_name = "d3-studio-assets-1660843754077"
bucket_name = os.environ.get("bucket_name")


def rand_prefix():
    return str(uuid.uuid4().hex[:6])


def upload_asset(local_file_path, filename, overwrite=False):
    aws_access_key_id = os.environ.get("s3_aws_access_key_id")
    aws_secret_access_key = os.environ.get("s3_aws_secret_access_key")
    s3_resource = boto3.resource("s3",
                                 region_name="us-west-1",
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key)
    bucket = s3_resource.Bucket(bucket_name)
    if overwrite:
        file_key = filename
    else:
        file_key = rand_prefix() + "_" + filename
    # TODO make private after test
    # upload_response = bucket.upload_file(Filename=local_file_path, Key=file_key)
    upload_response = bucket.upload_file(Filename=local_file_path, Key=file_key, ExtraArgs={'ACL': "public-read"})
    logging.info(f"Uploaded to S3 with response: {upload_response}")
    return file_key


