#
from dotenv import load_dotenv
import os
load_dotenv()

S3_BASE_URL = "https://d3-studio-assets-1660843754077.s3.us-west-1.amazonaws.com/"
JWT_SECRET_KEY = os.environ.get("jwt_secret_key")
MAX_FILE_SIZE_BYTES = int(10e6)

