# 04 – Secure Serverless API (WAF + Cognito + KMS + VPC Endpoints + Alarms)

## Business scenario
A product team exposes an API used by a mobile app. Requirements:
- All endpoints authenticated
- Protect against common web attacks and abusive traffic
- Encrypt data at rest and in transit
- Private access to AWS services from Lambda (no public egress required)
- Strong monitoring and alerting

This project deploys a hardened API:
- API Gateway (REST) integrated with Lambda
- Cognito User Pool authorizer
- WAFv2 Web ACL for rate limiting and baseline protections
- KMS key for encrypting secrets/config
- VPC with interface endpoints for AWS services (logs, sts, kms) to keep Lambda private
- CloudWatch alarms + SNS for errors/throttles

## Architecture
```mermaid
flowchart LR
  User[Client App] --> WAF[WAFv2]
  WAF --> API[API Gateway]
  API --> AUTH[Cognito Authorizer]
  API --> L[Lambda (in VPC)]
  L --> KMS[KMS]
  L --> CW[CloudWatch Logs]
  subgraph VPC
    L
    EP1[VPC Endpoint: logs]
    EP2[VPC Endpoint: sts]
    EP3[VPC Endpoint: kms]
  end
```

## What gets deployed
- VPC (2 private subnets)
- Interface endpoints: CloudWatch Logs, STS, KMS
- KMS key + alias
- Cognito user pool + app client
- Lambda function (Python) with minimal IAM
- API Gateway REST API with Cognito authorizer
- WAFv2 Web ACL (rate-based rule + AWS managed baseline)
- Alarms: 5XX rate, Lambda errors, throttles + SNS email alerts

## Deploy

> **Important:** SNS email subscriptions require confirmation. After `terraform apply`, check your inbox and confirm the subscription.

```bash
cd iac/terraform/envs/dev
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

## Validate
1. Sign up a user in Cognito (CLI or console), confirm login works
2. Call API without token → 401
3. Call API with token → 200 + JSON response
4. Trigger WAF rate limit (burst requests) → 429 responses
5. Check CloudWatch:
   - Lambda logs exist
   - Alarms are green

Validation checklist: `docs/Validation-Checklist.md`

## Artifacts
- Threat model: `docs/Threat-Model.md`
- Runbook: `docs/Runbook.md`
- Lambda code: `lambda/app.py`
