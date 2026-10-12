"""Cognito-authenticated, strictly validated, idempotent request writes."""
import base64
import hashlib
import json
import logging
import os
import re

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
MAX_BODY = 4096
ACTIONS = {"create", "update", "review"}
ID = re.compile(r"[A-Za-z0-9_-]{1,64}")
KEY = re.compile(r"[A-Za-z0-9_-]{16,64}")


def response(code, body):
    return {"statusCode": code, "headers": {"Content-Type": "application/json", "Cache-Control": "no-store"}, "body": json.dumps(body)}


def object_without_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_field")
        result[key] = value
    return result


def request_headers(event):
    result = {}
    headers = event.get("headers")
    multiple = event.get("multiValueHeaders")
    headers = {} if headers is None else headers
    multiple = {} if multiple is None else multiple
    if not isinstance(headers, dict) or not isinstance(multiple, dict):
        raise ValueError("invalid_headers")
    for key, value in headers.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("invalid_headers")
        name = key.lower()
        if name in result:
            raise ValueError("ambiguous_header")
        result[name] = value
    seen = set()
    for key, values in multiple.items():
        if not isinstance(key, str) or not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], str):
            raise ValueError("ambiguous_header")
        name = key.lower()
        if name in seen or (name in result and result[name] != values[0]):
            raise ValueError("ambiguous_header")
        seen.add(name)
        result[name] = values[0]
    return result


def parse_request(event):
    if event.get("httpMethod") != "POST":
        raise ValueError("invalid_method")
    raw = event.get("body")
    if not isinstance(raw, str) or len(raw) > MAX_BODY * 2:
        raise ValueError("invalid_body")
    encoded = event.get("isBase64Encoded", False)
    if not isinstance(encoded, bool):
        raise ValueError("invalid_encoding_flag")
    try:
        if encoded:
            raw = base64.b64decode(raw, validate=True).decode("utf-8")
        if len(raw.encode("utf-8")) > MAX_BODY:
            raise ValueError("body_too_large")
    except (UnicodeError, base64.binascii.Error):
        raise ValueError("invalid_body") from None
    try:
        body = json.loads(raw, object_pairs_hook=object_without_duplicates)
    except (ValueError, RecursionError):
        raise ValueError("invalid_json") from None
    if not isinstance(body, dict) or set(body) != {"customer_id", "action"}:
        raise ValueError("invalid_fields")
    if not isinstance(body["customer_id"], str) or not ID.fullmatch(body["customer_id"]):
        raise ValueError("invalid_customer_id")
    if not isinstance(body["action"], str) or body["action"] not in ACTIONS:
        raise ValueError("invalid_action")
    headers = request_headers(event)
    if headers.get("content-type", "").split(";")[0].strip().lower() != "application/json":
        raise ValueError("unsupported_content_type")
    key = headers.get("idempotency-key")
    if not isinstance(key, str) or not KEY.fullmatch(key):
        raise ValueError("invalid_idempotency_key")
    return body, key


def subject_from_event(event):
    current = event
    for key in ("requestContext", "authorizer", "claims"):
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    subject = current.get("sub") if isinstance(current, dict) else None
    if not isinstance(subject, str) or not 1 <= len(subject) <= 128:
        return None
    try:
        subject.encode("utf-8")
    except UnicodeError:
        return None
    return subject


def handle(event, context, table):
    if not isinstance(event, dict):
        return response(400, {"error": "invalid_event"})
    subject = subject_from_event(event)
    if subject is None:
        return response(401, {"error": "unauthorized"})
    try:
        body, key = parse_request(event)
    except ValueError as exc:
        return response(400, {"error": str(exc)})
    request_id = hashlib.sha256((subject + ":" + key).encode()).hexdigest()
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    item = {"request_id": request_id, "owner_sub": subject, "payload_hash": digest, **body}
    try:
        table.put_item(Item=item, ConditionExpression="attribute_not_exists(request_id)")
    except Exception as exc:
        details = getattr(exc, "response", {})
        code = details.get("Error", {}).get("Code") if isinstance(details, dict) else None
        if code == "ConditionalCheckFailedException":
            try:
                existing = table.get_item(Key={"request_id": request_id}, ConsistentRead=True).get("Item")
            except Exception:
                return response(503, {"error": "temporarily_unavailable"})
            # Missing data after a conditional conflict is inconclusive, not a payload conflict.
            if not isinstance(existing, dict) or not existing:
                return response(503, {"error": "temporarily_unavailable"})
            if existing.get("owner_sub") == subject and existing.get("payload_hash") == digest:
                return response(200, {"request_id": request_id, "replayed": True})
            return response(409, {"error": "idempotency_conflict"})
        LOG.error("storage_failure", extra={"request_id": getattr(context, "aws_request_id", "unknown"), "error_code": str(code)})
        return response(503, {"error": "temporarily_unavailable"})
    LOG.info("request_created", extra={"request_id": getattr(context, "aws_request_id", "unknown")})
    return response(201, {"request_id": request_id, "replayed": False})


def handler(event, context):
    import boto3
    return handle(event, context, boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"]))
