import json


def hello(event, context):
    body = {
        "message": "Api Up and running!",
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
