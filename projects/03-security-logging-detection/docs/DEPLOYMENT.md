# Detection deployment

## Ownership and service prerequisites

Inspect the region for an existing GuardDuty detector and Security Hub account before apply. Set `create_guardduty=false` or `create_securityhub=false` when another configuration owns them. The pipeline can consume findings from those existing services without claiming ownership.

Check for the OpenSearch service-linked role. The default does not create it. Set `create_opensearch_service_role=true` only when it is absent and the sandbox can own it. Confirm the selected region supports the pinned engine version and chosen instance type. OpenSearch creation can take substantial time and begins ongoing charges.

## Post-apply checks

Confirm CloudTrail delivery, private domain endpoints, IAM/domain policies, Lambda VPC subnets, S3 gateway endpoint policy, EventBridge target permission, both queue policies/destinations and SNS subscription state. Confirm GuardDuty findings actually appear in Security Hub for your account; enablement alone is not end-to-end proof.

## Synthetic handler integration test

The fixture is intentionally synthetic. From the project root, after replacing its account/region identifiers if needed:

```bash
aws lambda invoke --function-name "$INGEST_FUNCTION" --cli-binary-format raw-in-base64-out --payload fileb://fixtures/securityhub-event.json response.local.json
```

This direct invocation tests the handler, archive and indexing path. It does **not** test EventBridge matching or SNS alert delivery. For that, use an approved Security Hub sample finding workflow in the sandbox and capture the actual imported finding event. Do not claim the direct invocation tested a rule it bypassed.

The fixture is a minimal internal event, not a complete ASFF object for `BatchImportFindings`. If using that API, construct a valid full ASFF finding including required fields and an account-owned product ARN. Avoid copying the minimal fixture directly into that API.

## Investigation access

S3 archive reads require a separate operator role; the ingestion role is intentionally write-only. OpenSearch data-plane search similarly needs an explicitly reviewed read principal, IAM permission, domain policy entry and private network/security-group path. Do not temporarily set Principal `*` or public access to view a dashboard.

Complete the acceptance ledger before calling this an operational detection system. Document which account/service owner will monitor queues and confirm the notification recipient.
