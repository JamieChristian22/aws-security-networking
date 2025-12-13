# 03 – Centralized Security Logging & Detection (CloudTrail + GuardDuty + Security Hub + OpenSearch)

## Business scenario
Security needs a practical detection pipeline that supports:
- Central visibility into API activity and security findings
- Queryable logs for investigations
- Alerts for high-severity threats

This project deploys:
- **Organization-ready baseline (single account deploy)** for:
  - CloudTrail → S3 + CloudWatch Logs
  - GuardDuty enabled
  - Security Hub enabled with standards
  - Findings streamed into **OpenSearch** for dashboards
- CloudWatch alarms + SNS notifications for high-severity events

## Architecture
```mermaid
flowchart TB
  CT[CloudTrail] --> S3[(S3 Log Archive)]
  CT --> CW[CloudWatch Logs]
  GD[GuardDuty] --> SH[Security Hub]
  SH --> EB[EventBridge Rule]
  EB --> OS[OpenSearch Ingestion (Lambda)]
  OS --> DSH[OpenSearch Dashboards]
  EB --> SNS[SNS Alerts]
```

## What gets deployed

### Security note
This project configures the OpenSearch access policy to **only allow the IAM principal running Terraform** (secure by default). If you need broader access, update the policy to allow specific approved role/user ARNs, or place the domain in a VPC.

- CloudTrail + S3 bucket (versioned + blocked public access)
- GuardDuty detector
- Security Hub + AWS Foundational Security Best Practices standard
- EventBridge rules for:
  - Security Hub findings HIGH/CRITICAL → SNS
  - Security Hub findings → Lambda → OpenSearch (indexing)
- OpenSearch domain (t3.small.search, encryption enabled)
- Lambda function for ingestion (Python), least-privilege IAM role

## Deploy

> **Important:** SNS email subscriptions require confirmation. After `terraform apply`, check your inbox and confirm the subscription.

```bash
cd iac/terraform/envs/dev
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

## Validate
- Generate a test Security Hub finding:
  - Enable an AWS Config rule that fails (optional), or
  - Run a GuardDuty sample findings command
- Confirm:
  - Email alert received for HIGH findings
  - Finding document appears in OpenSearch index `securityhub-findings-*`

Validation checklist: `docs/Validation-Checklist.md`

## Artifacts
- Threat model: `docs/Threat-Model.md`
- Runbook: `docs/Runbook.md`
- Lambda code: `lambda/ingest_securityhub.py`
