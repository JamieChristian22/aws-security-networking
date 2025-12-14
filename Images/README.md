# 📸 AWS Deployment Evidence – Images

This directory contains **AWS console screenshots** that verify the real-world deployment and validation of the infrastructure, security, and serverless components referenced throughout this repository.

These images serve as **proof of hands-on implementation**, not simulations or diagrams.

---

## 🌐 Networking & VPC Security

### Web Application Security Group
- Demonstrates inbound traffic controls for HTTP (80) and HTTPS (443)
- Scoped to a specific VPC
- Illustrates security group–based network perimeter enforcement

**AWS Services:** Amazon VPC, Security Groups

---

## 🔐 Identity & Access Management (IAM)

### IAM Policies
- Custom IAM policies created
- Permissions scoped using least-privilege principles
- Policies aligned to service-specific access needs

### IAM Roles
- Service roles created for Lambda, API Gateway, SQS, and DynamoDB
- Trust relationships configured correctly
- Separation of duties enforced

**AWS Services:** IAM Policies, IAM Roles

---

## ⚙️ Serverless & Event-Driven Architecture

### AWS Lambda Function
- Lambda function deployed successfully
- Configured with appropriate runtime and permissions
- Integrated with downstream services

### Lambda Trigger (Amazon SQS)
- Event-driven processing using SQS
- Decoupled ingestion and processing layers
- Demonstrates scalable serverless design

**AWS Services:** AWS Lambda, Amazon SQS

---

## 🗄️ Data & Analytics Pipeline

### Amazon RDS – PostgreSQL
- Managed PostgreSQL instance provisioned
- Used for structured data persistence
- Encrypted and deployed in AWS region

### Amazon Athena
- External tables created over S3-backed data
- SQL queries executed successfully
- Enables serverless analytics on ingested data

### Amazon API Gateway
- POST ingestion endpoint configured
- Integrated with backend services
- Deployed and tested

**AWS Services:** API Gateway, Amazon S3, Athena, Amazon RDS

---

## 🧠 Why These Images Matter

These screenshots confirm that the projects in this repository are:

- ✅ **Deployed in AWS**
- ✅ **Security-focused (IAM, SGs, least privilege)**
- ✅ **Production-aligned architectures**
- ✅ **End-to-end tested**

They provide transparency and validation for the architectural and security decisions documented elsewhere in this repository.

---

## 🔗 Usage

These images are referenced in:
- The root `README.md`
- Individual project documentation
- Portfolio walkthroughs and interview explanations
