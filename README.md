# 🔐 AWS Security + Networking Portfolio

![AWS](https://img.shields.io/badge/AWS-Security%20%2B%20Networking-232F3E?logo=amazonaws&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-Infrastructure%20as%20Code-844FBA?logo=terraform&logoColor=white)
![Python](https://img.shields.io/badge/Python-Security%20Automation-3776AB?logo=python&logoColor=white)
![IAM](https://img.shields.io/badge/IAM-Zero%20Trust-success)
![Status](https://img.shields.io/badge/Status-Portfolio%20Ready-brightgreen)

An enterprise-style AWS security and networking portfolio demonstrating **segmented network architecture, centralized inspection, zero-trust IAM guardrails, centralized detection engineering, secure serverless design, infrastructure as code, operational runbooks, validation, and evidence-based security controls**.

## Portfolio Projects

| Project | Focus |
|---|---|
| `01-network-core` | Hub/spoke VPC architecture, Transit Gateway, centralized egress inspection, AWS Network Firewall, flow logs |
| `02-iam-guardrails` | Permission boundaries, least-privilege roles, break-glass access, SCP policy pack, IAM monitoring |
| `03-security-logging-detection` | CloudTrail, GuardDuty, Security Hub, EventBridge, OpenSearch, SNS, detection pipeline |
| `04-secure-serverless-api` | API Gateway, Cognito, WAF, Lambda, DynamoDB, KMS, VPC endpoints, alarms |

## Security Engineering Lifecycle

```text
Business Requirement
        ↓
Threat Model
        ↓
Security Architecture
        ↓
Preventive Controls
        ↓
Detective Controls
        ↓
Terraform
        ↓
Validation
        ↓
Operational Runbook
        ↓
Evidence
        ↓
Continuous Improvement
```

## Recruiter Quick Start

**Networking:** start with `projects/01-network-core/README.md`  
**Identity / IAM:** start with `projects/02-iam-guardrails/README.md`  
**Detection Engineering:** start with `projects/03-security-logging-detection/README.md`  
**Application Security:** start with `projects/04-secure-serverless-api/README.md`

## Design Principles

- Default-deny where practical.
- No public data tiers unless explicitly required.
- Human access uses federation/MFA concepts and short-lived roles.
- Workloads use roles instead of long-lived access keys.
- Sensitive services use KMS encryption.
- Security findings are centralized and actionable.
- Network paths are explicit and inspectable.
- Infrastructure is reproducible through Terraform.
- Every project includes threat modeling, validation, runbooks, and evidence.
- Any benchmark, cost, or test result not executed in a live AWS account is labeled modeled or simulated.

## Technologies Demonstrated

**VPC • Transit Gateway • AWS Network Firewall • NAT Gateway • VPC Flow Logs • IAM • Permission Boundaries • SCPs • CloudTrail • GuardDuty • Security Hub • EventBridge • OpenSearch • SNS • API Gateway • Cognito • AWS WAF • Lambda • DynamoDB • KMS • VPC Endpoints • CloudWatch • Terraform • Python**

## Portfolio Scope

This repository contains simulated enterprise security engagements and reference implementations. It does not claim a live production deployment unless deployment evidence is explicitly provided. Modeled cost/security outcomes are not represented as realized customer outcomes.
