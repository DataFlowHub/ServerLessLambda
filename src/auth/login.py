import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json
import os


#These ID's are for the test cognito pool
#USER_POOL_ID =
#CLIENT_ID =
#CLIENT_SECRET =

def get_secret_hash(username):
    msg = username + os.getenv("COGNITO_CLIENT_ID")
    dig = hmac.new(str(os.getenv("COGNITO_CLIENT_SECRET")).encode('utf-8'), msg=str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2

def initiate_auth(client, username, password):
    secret_hash = get_secret_hash(username)
    try:
        resp = client.admin_initiate_auth(
            UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
            ClientId=os.getenv("COGNITO_CLIENT_ID"),
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'SECRET_HASH': secret_hash,
                'PASSWORD': password,
            },
            ClientMetadata={
                'username': username,
                'password': password,
            })
    except client.exceptions.NotAuthorizedException:
        return None, "The username or password is incorrect"
    except client.exceptions.UserNotConfirmedException:
        return None, "User is not confirmed"
    except Exception as e:
        return None, e.__str__()

    return resp, None


def lambda_handler(event, context):
    headers = event["headers"]
    continueflow = False
    try:
        if "Content-Type" in headers:
            if "application/json" in headers["Content-Type"]:
                continueflow = True
        if "content-type" in headers:
            if "application/json" in headers["content-type"]:
                continueflow = True

        if continueflow == True:
            body = event["body"]
            body = body.replace("\'", "\"")
            jsondata = json.loads(body)
        else:
            return {
                "statusCode": 500,
                "body": "Content-type need be: application/json, we only allow json requests"
            }
    except KeyError as ke:
        return {
            "statusCode": 500,
            "body": "Content-type need be: application/json, we only allow json requests"
        }

    client = boto3.client('cognito-idp')
    try:
        for field in ["username", "password"]:
            if jsondata[field] is None:
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "error": True,
                        "success": False,
                        "message": f"{field} is required",
                        "data": None
                    })
                }
    except KeyError:
        return {
            "statusCode": 500,
            "body": "Username and Password required"
        }

    resp, msg = initiate_auth(client, jsondata['username'], jsondata['password'])
    if msg != None:
        return {
            "statusCode": 200,
            "body": json.dumps({
                'message': msg,
                "error": True,
                "success": False,
                "data": None
            })
        }
    if resp.get("AuthenticationResult"):
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "success",
                "error": False,
                "success": True,
                "data": {
                    "id_token": resp["AuthenticationResult"]["IdToken"],
                    "refresh_token": resp["AuthenticationResult"]["RefreshToken"],
                    "access_token": resp["AuthenticationResult"]["AccessToken"],
                    "expires_in": resp["AuthenticationResult"]["ExpiresIn"],
                    "token_type": resp["AuthenticationResult"]["TokenType"]
                }
            })
        }

    else:  # this code block is relevant only when MFA is enabled
        return {
            "statusCode": 200,
            "body": json.dumps({
                "error": True,
                "success": False,
                "data": None,
                "message": None
            })
        }
