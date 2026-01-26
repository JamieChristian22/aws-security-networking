# AWS Security + Networking Portfolio (Job-Ready)

This repo contains **4 real-world AWS security & networking projects** designed to mirror what cloud/security engineers do in production: segmented networks, centralized security logging, serverless hardening, and identity governance.

Each project is **fully written (no TODOs)** and includes:
- A clear business scenario + security requirements
- Architecture diagram (Mermaid)
- Terraform IaC (modules + environments)
- Validation steps + threat model + runbook
- Cost notes + guardrails

> Date built: 2025-12-13

## Projects
1. **01 – Secure Multi-Account Network Core (Hub/Spoke + Inspection VPC + AWS Network Firewall)**
2. **02 – IAM Zero-Trust Guardrails (SCPs, Permission Boundaries, Break-Glass, Least-Privilege Roles)**
3. **03 – Centralized Security Logging & Detection (CloudTrail + GuardDuty + Security Hub + OpenSearch Dashboards)**
4. **04 – Secure Serverless API (Private access, WAF, Cognito, KMS, VPC endpoints, CloudWatch alarms)**

## Quick start (local)
Prereqs:
- Terraform >= 1.6
- AWS CLI v2 authenticated (`aws sts get-caller-identity`)
- A dedicated AWS account per environment is recommended.

Common workflow:
```bash
cd projects/01-network-core/iac/terraform/envs/dev
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

## Safety
These projects create AWS infrastructure. Always deploy into a sandbox account and set AWS Budgets.


## Evidence of Deployment

### AWS Secure Clickstream Ingestion Pipeline
Secure, serverless ingestion of application clickstream data using **API Gateway, S3, Athena, and PostgreSQL (RDS)**, with logging and access controls.

**Validated in AWS Console**
- RDS PostgreSQL instance successfully provisioned (us-east-1)
- Athena external table created over S3 clickstream data (JSON SerDe) and query executed successfully
- API Gateway `POST /` method configured and deployed for ingestion

📁 Suggested location for the project (if you add the code here): `projects/aws-secure-clickstream-ingestion/`


## Repo Structure
- `projects/<nn>-<name>/README.md` – scenario, architecture, how to deploy & validate
- `projects/<nn>-<name>/iac/terraform/` – production-style IaC (modules + envs)
- `projects/<nn>-<name>/docs/` – threat model, runbook, validation checklists
- `projects/<nn>-<name>/scripts/` – helper scripts (AWS CLI), optional

## License
MIT (see `LICENSE`)
