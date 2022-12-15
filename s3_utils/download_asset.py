import boto3
from dotenv import load_dotenv
import os
load_dotenv()
import logging

# bucket_name = "d3-studio-assets-1660843754077"
bucket_name = os.environ.get("bucket_name")


def download_asset(file_key):
    aws_access_key_id = os.environ.get("s3_aws_access_key_id")
    aws_secret_access_key = os.environ.get("s3_aws_secret_access_key")
    s3_resource = boto3.resource("s3",
                                 region_name="us-west-1",
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key)
    tmp_fpath = f'/tmp/{file_key}'
    _download_response = s3_resource.Object(bucket_name, file_key).download_file(tmp_fpath)
    logging.info(f"download with response: {_download_response}")
    return tmp_fpath


