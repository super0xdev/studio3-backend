# DStudio Account and Asset Management API

API BASE URL: https://j0624ut64a.execute-api.us-east-1.amazonaws.com/

S3 BASE URL: https://d3-studio-assets-1660843754077.s3.us-west-1.amazonaws.com/

## Features
1) Web3 Authentication 
2) SQL Server integration 
3) S3 Filestorage Integration for arbitrary file-types

## Endpoints

Currently, all endpoints are implemented as POST requests. All endpoints take jsonified parameters in the request 
body except for the /upload_asset endpoint which takes a FormData() object.

- `/login`
  - Parameters: 
    - address: str 
    - timestamp: int 
    - signature: str (b58 encoded)
  - Returns: 
    - token (jwt token to be included in x-access-tokens header for all authorized endpoints)
- `/update_profile`
  - Parameters: 
    - username: str
    - email: str
- `/upload_asset`
  - Parameters: 
    - FormData() object with a single `image` field. 
- `/overwrite_asset`
  - Parameters:
    - FormData() object with a single `image` field. 
    - asset_uid: int (of existing asset as form parameter)
    - file_key: str (of existing asset as form parameter)
- `/duplicate_asset`
  - Parameters:
    - asset_uid: int (of existing asset, can be owned by different user)
- `/delete_asset`
  - Parameters:
    - asset_uid: int (of existing asset as form parameter)
    - file_key: str (of existing asset as form parameter)
- `/update_asset_metadata`
  - Parameters: 
    - asset_uid: int
    - transaction_signature: str
    - file_name: str
    - purchase_type: str
    - confirmed: bool
    - confirmation_timestamp: int (optional)
- `/download_asset`
  - Parameters:
    - file_path: str (corresponds to `file_key` returned by /list_assets endpoint)
  - Returns:
    - File binary data in `contents` of response (if non-json file type)
    - JSON object in `data` field of response (if json file type)
- `/list_assets`
  - Parameters:
    - Automatically extracts user_uid from jwt header
  - Returns:
    - JSON encoded array of Asset objects in the `data` field of response. 
      - Complete set of values included in each Asset object can be found in the data model located in `/tables/tables/Assets.py`

## Notes

- All endpoints other than login are authenticated via the `user_uid` value in the JWT upon login.
- Response and error codes can be found in the `/response_utils` directory.
- Client code examples can be found in the `tests` folder.
- This system is currently deployed as AWS Lambda functions using the Serverless Framework 

