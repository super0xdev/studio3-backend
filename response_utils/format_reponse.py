import json


def format_response(success, response_code):
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"success": success, 'code': response_code})
    }
    return response
