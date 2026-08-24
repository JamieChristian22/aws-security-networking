import json, os, urllib.request

INDEX_NAME = os.getenv("INDEX_NAME","security-findings")

def normalize(detail):
    finding = detail.get("findings",[{}])[0] if "findings" in detail else detail
    return {
        "id": finding.get("Id") or detail.get("id"),
        "title": finding.get("Title") or detail.get("detail-type"),
        "severity": (finding.get("Severity") or {}).get("Label","UNKNOWN"),
        "account": finding.get("AwsAccountId") or detail.get("account"),
        "region": finding.get("Region") or detail.get("region"),
        "resource": finding.get("Resources",[]),
        "raw": detail
    }

def handler(event, context):
    doc=normalize(event.get("detail",event))
    print(json.dumps({"index":INDEX_NAME,"document":doc}))
    return {"statusCode":200,"body":json.dumps({"normalized":True,"id":doc["id"]})}
