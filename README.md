# 🔐 AWS Security & Networking Portfolio

**Author:** Jamie Christian II  
**Region:** us-east-1  
**Email:** Jamiechristian557@gmail.com  
**GitHub:** https://github.com/JamieChristian22

Welcome to my **AWS Security & Networking portfolio** — a collection of real, deployed, security-focused cloud projects built using Terraform and validated directly in the AWS Console.

This repository demonstrates hands-on experience in:
- Secure network architecture
- Identity & access governance
- Detection & analytics pipelines
- Serverless security

---

## 📁 Projects

The main portfolio folder contains multiple production-relevant projects:

📂 **aws-security-networking-portfolio/**

Inside it you’ll find:

### 🔹 Secure Network Core
Hub-and-spoke VPC design with centralized inspection and egress control.  
**Focus:** Transit Gateway, AWS Network Firewall, VPC Flow Logs.

---

### 🔹 IAM Zero-Trust Guardrails
Identity governance with permission boundaries, break-glass access, and CloudTrail alerting.  
**Focus:** IAM policies, roles, least privilege.

---

### 🔹 Centralized Logging & Detection
Security telemetry pipeline with GuardDuty, Security Hub, EventBridge, and OpenSearch.  
**Focus:** Detection engineering and alert automation.

---

### 🔹 Secure Serverless API
API Gateway + Cognito + WAF with private Lambda and VPC endpoints.  
**Focus:** Application security and serverless best practices.

---

## 🔍 Evidence of Deployment (AWS Console)

This repository includes **verified AWS console screenshots** that prove real infrastructure deployment.

📁 **Evidence Location:** `Images/`

Validated components include:
- VPC security groups and networking
- IAM policies and service roles
- Lambda functions with SQS triggers
- API Gateway POST endpoints
- Amazon RDS (PostgreSQL)
- Amazon Athena queries over S3 data

These artifacts demonstrate that the projects are **deployed, tested, and observable**.

---

## 🛠 Technologies & Skills

**AWS Services**
- VPC, Transit Gateway, Network Firewall
- IAM Policies & Roles
- CloudTrail, GuardDuty, Security Hub
- EventBridge, OpenSearch
- Lambda, API Gateway, Cognito, WAF
- Athena, S3, RDS (PostgreSQL)
- SNS, CloudWatch

**Security Domains**
- Network Security
- Identity & Access Management
- Detection Engineering
- Incident Response
- Secure Serverless Architecture
- Infrastructure as Code (Terraform)

---

## 🚀 Deployment (Example)

Each project includes its own README with full deployment instructions.

```bash
cd aws-security-networking-portfolio/projects/01-network-core/iac/terraform/envs/dev
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

> ⚠️ SNS email subscriptions require confirmation after deployment.

---

## 📬 Contact

**Jamie Christian II**  
📧 Jamiechristian557@gmail.com  
🌐 https://github.com/JamieChristian22

---

⭐ **Tip:** Pin this repository on your GitHub profile to showcase real, deployable AWS security engineering work.
