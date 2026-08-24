# 04 — Secure Serverless API

A secure application architecture using **API Gateway, Cognito, AWS WAF, Lambda, DynamoDB, KMS, VPC endpoints, CloudWatch, CloudTrail, and least-privilege IAM**.

## Architecture

```mermaid
flowchart LR
USER[Client] --> COG[Cognito]
USER --> WAF[AWS WAF]
WAF --> API[API Gateway]
API --> AUTH[Cognito Authorizer]
API --> L[Lambda]
L --> DDB[(DynamoDB)]
L --> KMS[KMS]
L --> LOG[CloudWatch Logs]
CT[CloudTrail] --> AUDIT[(Audit)]
```

## Security Objectives
- authenticated requests only for protected routes
- throttling/rate controls at the edge
- least-privilege Lambda role
- encrypted DynamoDB and logs
- no secrets in source code
- input validation
- actionable alarms
- incident/recovery procedures
