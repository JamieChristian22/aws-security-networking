import json
import os
import time
import urllib3
from datetime import datetime

http = urllib3.PoolManager()

OPENSEARCH_ENDPOINT = os.environ["OPENSEARCH_ENDPOINT"].rstrip("/")
INDEX_PREFIX = os.environ.get("INDEX_PREFIX", "securityhub-findings")
TIME_FIELD = os.environ.get("TIME_FIELD", "CreatedAt")

def _index_name(event_time: str) -> str:
    # event_time example: 2025-12-13T12:34:56.789Z
    dt = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
    return f"{INDEX_PREFIX}-{dt.strftime('%Y.%m.%d')}"

def handler(event, context):
    # EventBridge delivers Security Hub findings under detail.findings
    detail = event.get("detail", {})
    findings = detail.get("findings", [])

    if not findings:
        return {"statusCode": 200, "body": "No findings"}

    indexed = 0
    errors = 0

    for f in findings:
        event_time = f.get(TIME_FIELD) or f.get("UpdatedAt") or datetime.utcnow().isoformat() + "Z"
        index = _index_name(event_time)
        doc_id = f.get("Id") or str(int(time.time() * 1000))

        url = f"{OPENSEARCH_ENDPOINT}/{index}/_doc/{doc_id}"
        payload = json.dumps(f).encode("utf-8")

        resp = http.request(
            "PUT",
            url,
            body=payload,
            headers={"Content-Type": "application/json"},
            retries=False,
            timeout=10.0,
        )

        if 200 <= resp.status < 300:
            indexed += 1
        else:
            errors += 1

    return {"statusCode": 200, "indexed": indexed, "errors": errors}
