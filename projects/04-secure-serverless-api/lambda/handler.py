import json, os, boto3

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

def response(code, body):
    return {"statusCode": code, "headers":{"content-type":"application/json"}, "body":json.dumps(body)}

def handler(event, context):
    try:
        body=json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400,{"error":"invalid_json"})

    allowed={"customer_id","action"}
    if set(body)-allowed or not body.get("customer_id") or not body.get("action"):
        return response(400,{"error":"invalid_request"})

    item={
        "request_id":context.aws_request_id,
        "customer_id":body["customer_id"][:64],
        "action":body["action"][:64]
    }
    table.put_item(Item=item)
    return response(201,{"request_id":item["request_id"]})
