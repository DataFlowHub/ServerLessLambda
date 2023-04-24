import json
from mylayer import example

def hello(event, context):
    print(example.add_one(25))
    body = {
        "message": "Api Up and running!",
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }

def sayHello(event, context):
    print(example.add_one(15))

    body = {
        "message": "Saying Hello!",
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }

