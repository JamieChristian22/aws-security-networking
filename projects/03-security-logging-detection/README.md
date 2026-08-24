# 03 — Centralized Security Logging & Detection

A centralized detection-engineering architecture using **CloudTrail, GuardDuty, Security Hub, EventBridge, Lambda, OpenSearch, SNS, CloudWatch, and protected S3 log storage**.

## Detection Flow

```mermaid
flowchart LR
CT[CloudTrail] --> S3[(Log Archive)]
CT --> CW[CloudWatch Logs]
GD[GuardDuty] --> SH[Security Hub]
SH --> EB[EventBridge]
EB --> SNS[SNS]
EB --> L[Lambda Normalizer]
L --> OS[(OpenSearch)]
OS --> DASH[Dashboards]
```

## Goals
- central API audit visibility
- high/critical finding alerts
- searchable normalized findings
- evidence retention
- repeatable incident triage
- measurable detection coverage
