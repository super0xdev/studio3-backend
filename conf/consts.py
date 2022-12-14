#
from dotenv import load_dotenv
import os
load_dotenv()

# S3_BASE_URL = "https://d3-studio-assets-1660843754077.s3.us-west-1.amazonaws.com/"
S3_BASE_URL = "https://d3-studio-assets.s3.us-east-2.amazonaws.com/"

JWT_SECRET_KEY = os.environ.get("jwt_secret_key")
MAX_FILE_SIZE_BYTES = int(10e6)

ADMIN_WALLET_ADDRESS = "WX15ZcTF5ChwRh24pjnGw9JE3cgPDrn6mwDAL1bwhDL"
ADMIN_USER_UID = 5574987670839802979

