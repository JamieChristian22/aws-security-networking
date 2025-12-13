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
## 🔍 Evidence of Deployment (AWS Console)

This repository contains **verified AWS infrastructure deployments**, demonstrating hands-on experience with cloud security, networking, IAM, and serverless architectures.  
All components shown below were **created, configured, and validated directly in AWS**.

---

### 🌐 VPC & Network Security

**Web Application Security Group (WebAppSG)**  
- Explicit inbound rules for HTTP (80) and HTTPS (443)  
- Scoped to a specific VPC  
- Demonstrates security group–based perimeter enforcement

**AWS Services:** Amazon VPC, Security Groups

![VPC Security Group – WebAppSG](docs/evidence/VPC_SecurityGroup_WebAppSG.png)

---

### 🔐 Identity & Access Management (IAM)

**IAM Policies & Roles**
- Custom IAM policies created
- Least-privilege permissions enforced
- Service roles for Lambda, API Gateway, SQS, and DynamoDB
- Clear separation of duties via role-based access control (RBAC)

**AWS Services:** IAM Policies, IAM Roles

![IAM Policies](docs/evidence/iam-policies.png)  
![IAM Roles](docs/evidence/iam-roles.png)

---

### ⚙️ Serverless Compute & Event Processing

**AWS Lambda with SQS Integration**
- Lambda function deployed successfully
- Event-driven architecture using Amazon SQS
- IAM role attached for controlled service access
- Decoupled ingestion and processing layer

**AWS Services:** AWS Lambda, Amazon SQS

![Lambda with SQS Trigger](docs/evidence/lambda-sqs.png)

---

### 🗄️ Data & Analytics (Validated)

**PostgreSQL, Athena, and API Ingestion**
- Amazon RDS PostgreSQL instance provisioned
- API Gateway POST endpoint deployed and tested
- Clickstream data stored in S3 and queried via Athena external tables
- End-to-end ingestion and analytics pipeline validated

**AWS Services:** API Gateway, S3, Athena, RDS (PostgreSQL)

![RDS Created](docs/evidence/rds-created.png)  
![Athena Query Success](docs/evidence/athena-query-success.png)  
![API Gateway POST](docs/evidence/api-gateway-post.png)

---

### 🧠 Why This Matters

These screenshots confirm that the projects in this repository are:

- ✅ **Deployed in AWS (not simulated or diagram-only)**
- ✅ **Security-first (IAM, SGs, least privilege)**
- ✅ **Production-aligned architectures**
- ✅ **End-to-end tested and observable**

---

### 📁 Evidence Location

All deployment evidence is stored here:

```text
aws-security-networking-portfolio/docs/evidence/
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
