import json


def hello(event, context):
    body = {
        "message": "Api Up and running!",
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }

def sayHello(event, context):
    body = {
        "message": "Saying Hello!",
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }

