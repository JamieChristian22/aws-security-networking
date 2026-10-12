"""Archive-first Security Hub ingestion with bounded input and signed private writes."""
import hashlib
import json
import logging
import os
import re
from datetime import datetime, timezone
from urllib.request import Request, HTTPRedirectHandler, ProxyHandler, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
SEVERITIES = {"INFORMATIONAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
ENDPOINT = re.compile(r"vpc-[a-z0-9-]+\.[a-z]{2}(?:-[a-z]+)+-\d\.es\.amazonaws\.com")
ACCOUNT = re.compile(r"\d{12}")
MAX_FINDING_BYTES = 240_000


def normalize(finding):
    if not isinstance(finding, dict):
        raise ValueError("finding must be an object")
    limits = {"Id": 512, "ProductArn": 2048, "AwsAccountId": 12, "UpdatedAt": 64}
    for key, limit in limits.items():
        value = finding.get(key)
        if not isinstance(value, str) or not 1 <= len(value) <= limit:
            raise ValueError("invalid finding identity or timestamp")
    if not ACCOUNT.fullmatch(finding["AwsAccountId"]):
        raise ValueError("invalid AWS account")
    if not finding["ProductArn"].startswith("arn:aws:securityhub:") or ":product/" not in finding["ProductArn"]:
        raise ValueError("invalid product ARN")
    updated = datetime.fromisoformat(finding["UpdatedAt"].replace("Z", "+00:00"))
    if updated.tzinfo is None:
        raise ValueError("UpdatedAt requires a timezone")
    updated = updated.astimezone(timezone.utc)
    stamp = updated.isoformat()
    # A JSON tuple prevents separator ambiguity and scopes identity to the source account.
    identity = json.dumps([finding["ProductArn"], finding["AwsAccountId"], finding["Id"], stamp], separators=(",", ":"))
    doc_id = hashlib.sha256(identity.encode()).hexdigest()
    severity = finding.get("Severity", {})
    if not isinstance(severity, dict):
        raise ValueError("invalid severity")
    label = severity.get("Label", "INFORMATIONAL")
    if not isinstance(label, str) or label not in SEVERITIES:
        raise ValueError("invalid severity label")
    resources = finding.get("Resources", [])
    if not isinstance(resources, list) or len(resources) > 100 or any(not isinstance(r, dict) for r in resources):
        raise ValueError("invalid resource list")
    title = finding.get("Title", "")
    if not isinstance(title, str):
        raise ValueError("invalid title")
    record = {"finding_id": finding["Id"], "product_arn": finding["ProductArn"], "account_id": finding["AwsAccountId"], "region": finding.get("Region", "unknown"), "updated_at": stamp, "severity": label, "title": title[:256], "record_state": finding.get("RecordState", "ACTIVE"), "resources": resources}
    return "securityhub-" + updated.strftime("%Y.%m"), doc_id, record


def process(event, archive, index):
    if not isinstance(event, dict) or event.get("source") != "aws.securityhub" or event.get("detail-type") != "Security Hub Findings - Imported":
        raise ValueError("unsupported event")
    detail = event.get("detail")
    findings = detail.get("findings") if isinstance(detail, dict) else None
    if not isinstance(findings, list) or not findings or len(findings) > 100:
        raise ValueError("expected 1–100 findings")
    prepared = []
    # Reject malformed batches before side effects; runtime storage failures still replay
    # already completed versions safely because their identities are deterministic.
    for finding in findings:
        index_name, doc_id, record = normalize(finding)
        raw = json.dumps(finding, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        if len(raw) > MAX_FINDING_BYTES:
            raise ValueError("finding too large")
        prepared.append((index_name, doc_id, record, raw))
    for index_name, doc_id, record, raw in prepared:
        archive("findings/" + index_name + "/" + doc_id + ".json", raw)
        index(index_name, doc_id, json.dumps(record, sort_keys=True).encode())
    LOG.info("findings_indexed", extra={"count": len(prepared)})
    return {"indexed": len(prepared)}


def signed_put(session, endpoint, index_name, doc_id, payload, opener=None):
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    if not isinstance(endpoint, str) or not ENDPOINT.fullmatch(endpoint):
        raise ValueError("expected private commercial-region OpenSearch hostname")
    if not re.fullmatch(r"securityhub-\d{4}\.\d{2}", index_name) or not re.fullmatch(r"[a-f0-9]{64}", doc_id):
        raise ValueError("invalid document path")
    if not session.region_name or f".{session.region_name}.es.amazonaws.com" not in endpoint:
        raise ValueError("endpoint region mismatch")
    credentials = session.get_credentials()
    if credentials is None:
        raise RuntimeError("missing signing credentials")
    url = "https://" + endpoint + "/" + index_name + "/_doc/" + doc_id
    request = AWSRequest(method="PUT", url=url, data=payload, headers={"Content-Type": "application/json"})
    SigV4Auth(credentials.get_frozen_credentials(), "es", session.region_name).add_auth(request)
    signed = Request(url, data=payload, headers=dict(request.headers), method="PUT")
    # Do not forward signed headers via a proxy or redirect to another destination.
    transport = opener if opener is not None else build_opener(ProxyHandler({}), NoRedirect())
    with transport.open(signed, timeout=10) as result:
        if result.status not in (200, 201):
            raise RuntimeError("index write failed")


def handler(event, context):
    import boto3
    session = boto3.Session()
    s3 = session.client("s3")
    endpoint = os.environ["OPENSEARCH_ENDPOINT"]
    if not ENDPOINT.fullmatch(endpoint):
        raise ValueError("expected private commercial-region OpenSearch hostname")

    def archive(key, payload):
        s3.put_object(Bucket=os.environ["ARCHIVE_BUCKET"], Key=key, Body=payload, ContentType="application/json", ServerSideEncryption="AES256")

    def index(index_name, doc_id, payload):
        signed_put(session, endpoint, index_name, doc_id, payload)
    return process(event, archive, index)
