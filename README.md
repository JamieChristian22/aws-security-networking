# 🔐 AWS Security & Networking

**Author:** Jamie Christian II  
**Region:** us-east-1  
**Email:** Jamiechristian557@gmail.com  
**GitHub:** [JamieChristian22](https://github.com/JamieChristian22)

This repository contains my **AWS Security & Networking portfolio**, demonstrating real-world cloud security engineering through fully implemented projects.

Each project includes:
- Business context & security requirements  
- Architecture design  
- Terraform infrastructure (prod-style modules + environments)  
- Threat modeling  
- Operational runbooks  
- Validation checklists  

⚠️ These are **real deployable solutions**, not placeholders.

---

## 📁 Portfolio Overview

You’ll find all portfolio content in the main directory here:

📂 **[`aws-security-networking-portfolio/`](./aws-security-networking-portfolio)**

Inside that folder are **4 complete security projects**, each with its own structured folder.

---

## 🚀 Projects Included

### 1. **Secure Network Core**
Hub & spoke VPC design with centralized inspection and egress:
- Transit Gateway (TGW)  
- AWS Network Firewall  
- Centralized NAT  
- Flow logs to CloudWatch  

**Focus:** Network segmentation, controlled egress, traffic visibility

---

### 2. **IAM Zero-Trust Guardrails**
Identity governance with least-privilege controls:
- IAM permission boundaries  
- Break-glass admin role (MFA enforced)  
- CloudTrail + CloudWatch alarms  
- SCP examples

**Focus:** IAM security, privilege escalation prevention, alerting

---

### 3. **Centralized Security Logging & Detection**
Security telemetry and detection pipeline:
- Multi-region CloudTrail  
- GuardDuty + Security Hub  
- EventBridge driven events  
- OpenSearch for investigation

**Focus:** Cloud detection engineering, findings indexing, alerts

---

### 4. **Secure Serverless API**
Hardened API with defense-in-depth:
- API Gateway + WAFv2  
- Cognito authorizer  
- Lambda in private subnets  
- VPC endpoints + KMS  
- CloudWatch alarms

**Focus:** Application security, authentication, private connectivity

---

## 🛠 Tech & Security Skills Demonstrated

**AWS Services:**  
VPC, TGW, NAT, Network Firewall, Flow Logs  
IAM, CloudTrail, GuardDuty, Security Hub  
EventBridge, OpenSearch, Lambda  
API Gateway, WAFv2, Cognito, KMS  
CloudWatch, SNS

**Security Concepts:**  
Network security, IAM governance  
Detection engineering  
Incident response pipelines  
Secure serverless architecture  
Least privilege & logging

---

## 📌 How to Deploy

Each project contains its own README with instructions.

```bash
cd aws-security-networking-portfolio/projects/01-network-core/iac/terraform/envs/dev
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

> **Important:** SNS email alerts require you to confirm the subscription in your email after deployment.

---

## 📬 Contact

**Jamie Christian II**  
📧 Jamiechristian557@gmail.com  
🌐 github.com/JamieChristian22
