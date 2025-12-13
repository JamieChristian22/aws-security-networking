import json
import os
from datetime import datetime

def handler(event, context):
    # This lambda is designed to be used behind a Cognito authorizer.
    # API Gateway will pass authorizer claims under requestContext.
    claims = (
        event.get("requestContext", {})
            .get("authorizer", {})
            .get("claims", {})
    )

    username = claims.get("cognito:username", "unknown")
    now = datetime.utcnow().isoformat() + "Z"

    body = {
        "message": "Secure serverless API is running.",
        "user": username,
        "timestamp": now,
        "requestId": getattr(context, "aws_request_id", None),
    }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
