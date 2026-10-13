# 🛡️ AWS Security & Networking Portfolio

### Enterprise AWS Network Security | IAM Engineering | Threat Detection | Secure Serverless Architecture

**Jamie Christian II**  
Cloud Engineering • Cloud Security • AWS Infrastructure • Network Security • Security Operations

![AWS](https://img.shields.io/badge/AWS-Security_%26_Networking-232F3E?logo=amazonwebservices)
![Terraform](https://img.shields.io/badge/Terraform-1.9.8%2B-7B42BC?logo=terraform)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)
![Security](https://img.shields.io/badge/Focus-Defense_in_Depth-0F766E)
![Testing](https://img.shields.io/badge/Offline_Tests-186_Passed-238636)

---

## 📌 Executive Overview

The AWS Security & Networking Portfolio is a comprehensive cloud security engineering laboratory designed to demonstrate the implementation of secure AWS infrastructure, identity controls, threat detection, network segmentation, and protected serverless applications.

The portfolio consists of **four independently deployable AWS sandbox projects**, each addressing a distinct security engineering domain.

Rather than presenting isolated AWS configurations, the projects emphasize engineering practices used in professional cloud environments:

- Infrastructure as Code with Terraform
- Network segmentation and controlled routing
- Identity and access management
- Least-privilege authorization
- Security logging and detection pipelines
- Incident investigation and recovery
- Secure API design and application protection
- Automated testing and security validation
- Infrastructure reproducibility
- Operational runbooks and technical documentation

Each project includes a canonical Terraform configuration, architecture documentation, implementation guidance, threat assumptions, and a validation approach.

**Portfolio Objective:** Demonstrate the ability to design, explain, test, troubleshoot, and document AWS security solutions using engineering practices relevant to enterprise cloud environments.

> **Implementation transparency:** This repository contains implemented source code and documented offline testing. Live AWS deployment and production security effectiveness have not been independently verified. The repository distinguishes completed checks from blocked, pending, and unexecuted validation.

---

# 🏗️ 1. AWS Security Architecture

## 1.1 Portfolio Architecture

![AWS Security Portfolio Architecture](diagrams/portfolio.svg)

The portfolio is organized into four complementary security domains:

| Security Domain | Primary AWS Technologies | Engineering Objective |
|---|---|---|
| Network Security | VPC, Transit Gateway, AWS Network Firewall, NAT Gateway, VPC Flow Logs | Implement segmented networking and controlled traffic inspection |
| Identity Security | IAM, permission boundaries, MFA, CloudTrail, AWS Organizations | Enforce least privilege and strengthen administrative access |
| Security Monitoring | CloudTrail, GuardDuty, Security Hub, EventBridge, Lambda, OpenSearch | Collect, process, and investigate security events |
| Application Security | API Gateway, Cognito, AWS WAF, Lambda, DynamoDB | Protect API access, application processing, and stored data |

## 1.2 Architecture Principles

The designs are guided by six security engineering principles.

**1. Defense in Depth**

Multiple security controls are used to reduce reliance on any single protection mechanism.

**2. Least Privilege**

Identities and workloads should receive only the permissions necessary to perform authorized operations.

**3. Network Segmentation**

Resources are separated according to their intended network access and trust relationships.

**4. Secure-by-Design Infrastructure**

Security requirements are represented in version-controlled infrastructure configurations rather than relying exclusively on manual console changes.

**5. Operational Visibility**

Logging, monitoring, and failure-handling mechanisms are incorporated into the architecture.

**6. Evidence-Based Validation**

Security controls are evaluated through source inspection, automated tests, and planned runtime verification rather than assumed to be effective merely because they are configured.

### Architecture Scope

The four projects are independent, single-account AWS sandbox implementations.

They do not automatically establish an enterprise multi-account landing zone, delegated security administrator, or centralized cross-account log archive.

The network project uses multiple VPCs within one account. Optional organization-level controls require additional permissions and explicit deployment decisions.

---

# ☁️ 2. Project Portfolio

## 🌐 Project 01 — Enterprise AWS Network Security

**Directory:** [01-network-core](projects/01-network-core/README.md)

### Business Scenario

An organization needs to separate cloud workloads into controlled network segments while maintaining predictable routing, internet egress, traffic inspection, and operational visibility.

### Engineering Objectives

- Establish logically segmented VPC environments.
- Control connectivity between network segments.
- Inspect designated network traffic.
- Reduce unauthorized east-west communication.
- Support predictable outbound internet routing.
- Capture network traffic metadata for investigation.

### Implemented Design

The project defines:

- Three segmented VPCs
- AWS Transit Gateway connectivity
- Explicit routing controls
- Two-Availability-Zone Network Firewall design
- NAT-based internet egress
- VPC Flow Logs
- Network isolation and inspection patterns

### Key Security Decisions

**Explicit Transit Gateway Routing**

Default route propagation is disabled so connectivity must be deliberately configured.

**Cross-Spoke Isolation**

Explicit blackhole routes are used to prevent designated network segments from communicating directly.

**Availability Zone Alignment**

Egress paths are designed around Availability Zone-matched firewall endpoints and NAT gateways.

**Inspection Enforcement**

The architecture avoids an intentional fallback route that would bypass the firewall.

### Example Traffic Flow

```text
Application Workload
        |
        v
Spoke VPC Route Table
        |
        v
AWS Transit Gateway
        |
        v
Inspection / Egress VPC
        |
        v
AWS Network Firewall
        |
        v
NAT Gateway
        |
        v
Internet Gateway
        |
        v
External Destination
```

This diagram represents the intended outbound traffic path, not a measured live packet trace.

### Security Validation

Recommended checks include:

| Test | Expected Result |
|---|---|
| Authorized outbound connection | Traffic follows the approved egress path |
| Prohibited spoke-to-spoke connection | Traffic is blocked |
| Route-table inspection | No unauthorized bypass routes |
| Firewall inspection | Intended rules are applied |
| Flow-log review | Relevant traffic metadata is available |
| Availability Zone review | Routing follows intended AZ-specific paths |

These are acceptance objectives. Their live execution must be verified separately.

### Troubleshooting Scenarios

**Scenario: An application cannot access an approved external service.**

Investigation procedure:

1. Verify source subnet and associated route table.
2. Inspect Transit Gateway route tables.
3. Confirm the expected firewall endpoint path.
4. Review Network Firewall policy rules.
5. Inspect NAT Gateway and internet gateway routing.
6. Examine VPC Flow Logs for relevant traffic.
7. Document the cause and corrective action.

**Scenario: Traffic unexpectedly crosses network boundaries.**

Review route propagation, explicit routes, security group permissions, network ACLs, and firewall enforcement.

### Technical Documentation

- [Architecture and Packet Walkthrough](projects/01-network-core/docs/ARCHITECTURE.md)
- [Project README](projects/01-network-core/README.md)

### Skills Demonstrated

AWS Networking • Network Segmentation • Routing Analysis • Firewall Architecture • Cloud Troubleshooting • Infrastructure as Code

---

## 🔐 Project 02 — AWS IAM Security & Access Governance

**Directory:** [02-iam-guardrails](projects/02-iam-guardrails/README.md)

### Business Scenario

An organization must protect sensitive AWS resources while reducing excessive permissions, controlling privileged access, and maintaining visibility into identity-related activities.

### Engineering Objectives

- Implement least-privilege access.
- Restrict sensitive IAM operations.
- Define explicit role trust relationships.
- Protect emergency administrative access.
- Support auditability.
- Introduce optional organization-level restrictions.

### Implemented Design

The project includes:

- IAM permission boundaries
- Explicit allow-and-deny controls
- IAM role trust configurations
- Restrictions on routine IAM administration
- MFA requirements for emergency access
- Session-duration limitations
- Audit logging considerations
- Optional Service Control Policy configuration

### IAM Authorization Model

```text
Authenticated Principal
          |
          v
Identity-Based Permissions
          |
          v
Permission Boundary
          |
          v
Applicable Organization Controls
          |
          v
Resource Policy / Other Controls
          |
          v
AWS Authorization Decision
```

The actual AWS authorization decision depends on the applicable policy types, explicit denies, session context, and resource-specific evaluation rules.

### Security Engineering Decisions

**Permission Boundaries**

Permission boundaries establish an upper limit on permissions available to the affected IAM identity.

**Explicit Deny Rules**

Sensitive operations can be explicitly denied to reduce the risk of unintended privilege escalation.

**Role Trust Policies**

Role assumption is restricted according to the intended identity and service relationships.

**Emergency Access**

Emergency access uses separate trust controls, MFA requirements, and a maximum session duration of one hour.

### Security Validation Matrix

| Test Case | Expected Result |
|---|---|
| Authorized service operation | Allowed |
| Unauthorized IAM modification | Denied |
| Role assumption by unauthorized principal | Denied |
| Emergency access without required MFA | Denied |
| Authorized emergency session | Subject to configured controls |
| Restricted action outside permission boundary | Denied |

### Troubleshooting Scenarios

**Scenario: A legitimate application receives AccessDenied.**

Investigation procedure:

1. Identify the requesting principal.
2. Identify the denied API action.
3. Review identity-based permissions.
4. Examine permission boundaries.
5. Inspect applicable SCPs.
6. Check resource policies and role trust conditions.
7. Review CloudTrail events where available.
8. Correct the smallest necessary permission scope.
9. Retest authorized and unauthorized actions.

### Technical Documentation

- [IAM Architecture and Policy Evaluation](projects/02-iam-guardrails/docs/ARCHITECTURE.md)
- [IAM Project README](projects/02-iam-guardrails/README.md)

### Skills Demonstrated

AWS IAM • RBAC Concepts • Least Privilege • Access Governance • Policy Evaluation • Security Troubleshooting

---

## 🚨 Project 03 — AWS Security Logging & Threat Detection

**Directory:** [03-security-logging-detection](projects/03-security-logging-detection/README.md)

### Business Scenario

An organization requires centralized visibility into AWS security events and a repeatable method for collecting, processing, investigating, and retaining security findings.

### Engineering Objectives

- Capture AWS security activity.
- Integrate managed threat-detection services.
- Route findings into an event-processing pipeline.
- Protect access to security data.
- Support investigation and recovery.
- Handle failed processing without silently losing events.

### Implemented Design

The project incorporates:

- AWS CloudTrail
- Amazon GuardDuty
- AWS Security Hub
- Amazon EventBridge
- AWS Lambda
- Private Amazon OpenSearch
- Signed ingestion requests
- Archive handling
- Retry and dead-letter queue patterns

### Security Event Processing Architecture

```text
AWS Account Activity
         |
         v
CloudTrail / Security Services
         |
         v
GuardDuty / Security Hub Findings
         |
         v
Amazon EventBridge
         |
         v
AWS Lambda Processing
         |
         +------------------+
         |                  |
         v                  v
Private OpenSearch     Archive Storage
         |                  |
         v                  v
Security Analysis      Evidence Retention

Failures -> Retry / Failure Destination
```

The diagram is a logical representation of the project's detection and processing architecture.

### Security Engineering Decisions

**Private Search Infrastructure**

OpenSearch is configured for private VPC access rather than public internet exposure.

**Signed Requests**

The ingestion implementation uses AWS Signature Version 4 for authenticated requests.

**Restricted Ingestion Permissions**

The ingestion role is scoped to the required finding-document operations.

**Failure Propagation**

Failed archive or indexing operations raise errors to support configured retry and failure-handling behavior.

### Detection and Response Workflow

1. Security activity generates a relevant event or finding.
2. The event enters the configured processing path.
3. The ingestion function validates and transforms the event.
4. The event is delivered to the intended storage or analysis destination.
5. Processing failures trigger configured recovery mechanisms.
6. Analysts investigate suspicious activity using available evidence.
7. Findings, response actions, and lessons learned are documented.

### Validation Matrix

| Test | Expected Result |
|---|---|
| Valid finding received | Event processed successfully |
| Invalid event structure | Controlled error handling |
| Unauthorized OpenSearch request | Access denied |
| Indexing failure | Error propagated |
| Archive failure | Error propagated |
| Recoverable processing failure | Retry mechanism invoked |
| Persistent processing failure | Failure destination behavior evaluated |

### Troubleshooting Scenarios

**Scenario: Security findings are not appearing in OpenSearch.**

Investigation procedure:

1. Confirm the upstream finding source.
2. Inspect EventBridge rules and targets.
3. Review Lambda invocation metrics.
4. Inspect CloudWatch error logs.
5. Verify the ingestion role's permissions.
6. Check OpenSearch network access and request signing.
7. Review retry and failure-destination records.
8. Reprocess events only when safe and authorized.
9. Confirm that event identifiers and timestamps remain traceable.

### Technical Documentation

- [Detection and Recovery Runbook](projects/03-security-logging-detection/docs/RUNBOOK.md)
- [Project README](projects/03-security-logging-detection/README.md)

### Skills Demonstrated

Cloud Security Monitoring • Threat Detection • AWS Logging • Incident Investigation • Python Automation • Event Processing • Security Operations

---

## 🔌 Project 04 — Secure AWS Serverless API

**Directory:** [04-secure-serverless-api](projects/04-secure-serverless-api/README.md)

### Business Scenario

An organization needs to expose application functionality through an API while protecting user identities, validating requests, limiting abuse, and preventing unauthorized data operations.

### Engineering Objectives

- Implement authenticated API access.
- Enforce request validation.
- Restrict application permissions.
- Protect application data.
- Reduce duplicate processing.
- Introduce application-layer protections.
- Support operational monitoring and recovery.

### Implemented Design

The project includes:

- Amazon API Gateway
- Amazon Cognito
- AWS WAF
- AWS Lambda
- Amazon DynamoDB
- IAM execution permissions
- Private application processing
- DynamoDB point-in-time recovery
- Subject-scoped idempotency
- Input validation and action restrictions

### Application Architecture

```text
Authenticated API Client
           |
           v
         AWS WAF
           |
           v
    Amazon API Gateway
           |
           v
   Cognito Authorization
           |
           v
       AWS Lambda
           |
           v
 Request Validation
           |
           v
 IAM-Scoped Data Access
           |
           v
      DynamoDB Table
```

### Security Engineering Decisions

**Authentication Before Application Execution**

Cognito authorization is applied before requests reach the application handler.

**Input Validation**

Application requests are typed, size-limited, and restricted to supported actions.

**Least-Privilege Database Access**

The Lambda execution role is scoped to required DynamoDB operations.

**Idempotent Processing**

Conditional DynamoDB writes help prevent duplicate submissions.

Idempotency keys are associated with the authenticated subject to avoid inappropriate cross-user reuse.

**Data Recovery**

DynamoDB point-in-time recovery is incorporated into the design.

### API Security Validation Matrix

| Test Case | Expected Result |
|---|---|
| Valid authenticated request | Accepted |
| Missing or invalid authentication | Rejected |
| Unsupported action | Rejected |
| Malformed request body | Rejected |
| Oversized request | Rejected |
| Duplicate request | Controlled idempotent behavior |
| Conflicting replay | Rejected or handled according to contract |
| Unauthorized database operation | Denied |

### Troubleshooting Scenarios

**Scenario: An authorized user receives an unexpected API error.**

Investigation procedure:

1. Identify the request and response status.
2. Confirm the API Gateway route and method.
3. Review Cognito authorization results.
4. Inspect AWS WAF rules.
5. Review Lambda execution logs.
6. Validate the request schema.
7. Check IAM database permissions.
8. Inspect DynamoDB conditional-write results.
9. Reproduce the issue using a sanitized test request.
10. Document the root cause and regression test.

### Technical Documentation

- [API Contract](projects/04-secure-serverless-api/docs/API_CONTRACT.md)
- [Project README](projects/04-secure-serverless-api/README.md)

### Skills Demonstrated

API Security • Serverless Computing • AWS Lambda • Python • DynamoDB • Authentication • Authorization • Application Troubleshooting

---

# 🧪 3. Testing, Quality Assurance & Validation

The portfolio incorporates automated testing, static security checks, structural validation, and planned AWS acceptance testing.

## 3.1 Recorded Validation Results

The repository's release validation report documents the following results:

| Validation Category | Recorded Result | Status |
|---|---|---|
| Offline unit, property, SDK-emulation, and structural tests | 186 tests passed | PASS_OFFLINE |
| Lambda handler statement coverage | 100% across two handlers | PASS_OFFLINE |
| Lambda handler branch coverage | 100% across two handlers | PASS_OFFLINE |
| Targeted mutation checks | 8/8 detected | PASS_OFFLINE |
| Bandit Python security scan | Zero findings | PASS_OFFLINE |
| Repository consistency and local-link checks | Passed | PASS_OFFLINE |
| Terraform formatting and provider initialization | Completed in an earlier validation pass | Partial |
| Provider-backed Terraform validation | Blocked by provider execution restrictions | BLOCKED |
| Terraform mock-plan assertions | Not executed | NOT_RUN |
| Live AWS acceptance tests | 28 cases not executed | NOT_RUN |
| GitHub Actions CI execution | Not verified | BLOCKED |

**Important:** These are recorded results from the documented release, not evidence that the current repository has been independently retested.

### Coverage Interpretation

The reported 100% statement and branch coverage applies specifically to the two Python Lambda handlers.

The report records:

- 228 covered statements
- 96 covered branches
- 8 targeted mutation checks detected

These results do not establish 100% coverage of Terraform infrastructure, AWS integrations, IAM authorization behavior, network routing, or cloud security controls.

## 3.2 Validation Layers

| Level | Validation Type | Purpose |
|---|---|---|
| L1 | Source and configuration review | Examine implemented security controls |
| L2 | Static security analysis | Detect selected code and configuration issues |
| L3 | Unit and property testing | Verify local application behavior |
| L4 | SDK-emulated testing | Exercise AWS-related logic without live services |
| L5 | Terraform provider validation | Confirm provider schema and configuration compatibility |
| L6 | Terraform plan review | Inspect intended resource changes |
| L7 | Live AWS acceptance testing | Verify deployed behavior |
| L8 | Operational and security review | Evaluate recovery, monitoring, and security controls |

Only validation levels supported by actual recorded execution evidence should be represented as completed.

## 3.3 Evidence Integrity

The repository distinguishes:

- **PASS_OFFLINE:** Successfully executed local checks
- **BLOCKED:** Validation prevented by an environmental or execution limitation
- **NOT_RUN:** A planned check that has not been executed
- **PASS_LIVE:** A live test successfully executed with supporting evidence, when available

A planned test is not considered a passed test.

A successful Terraform plan is not considered proof of a successful deployment.

A configuration screenshot is not considered proof that a security control operated correctly.

### Validation References

- [Release Validation Report](reports/VALIDATION_REPORT.md)
- [Test Strategy](docs/TEST_STRATEGY.md)
- [Control-to-Test Traceability](docs/CONTROL_TEST_TRACEABILITY.csv)
- [Evidence Methodology](docs/EVIDENCE.md)

---

# ⚙️ 4. Getting Started

## 4.1 Prerequisites

Recommended local tools:

- Python 3.12
- Terraform 1.9.8 or a compatible reviewed version
- Git
- AWS CLI for authorized live AWS operations
- A dedicated AWS sandbox account for deployment
- Appropriate AWS permissions
- An environment capable of running Terraform provider plugins

Terraform provider versions are pinned for reproducibility. They should not be interpreted as automatically representing the latest available versions.

## 4.2 Clone the Repository

```bash
git clone https://github.com/JamieChristian22/aws-security-networking.git

cd aws-security-networking
```

## 4.3 Install Python Dependencies

```bash
python -m pip install -r requirements-dev.txt
```

For reproducible dependency management, review the included dependency lock file.

## 4.4 Run Offline Evidence Checks

```bash
make evidence
```

Review the generated reports and command exit statuses to determine which checks actually completed successfully.

## 4.5 Run Terraform Checks

```bash
make terraform-check
```

This target is intended for provider-backed checks using Terraform mock providers without creating AWS resources.

It requires an environment capable of running the configured Terraform provider plugins.

**Known limitation:** Provider-backed validation was blocked in the documented build environment by provider IPC socket restrictions.

## 4.6 Review Deployment Guidance

Before any AWS deployment:

1. Read the deployment documentation.
2. Review the selected project's Terraform variables.
3. Confirm the AWS account and Region.
4. Inspect IAM and networking implications.
5. Estimate resource costs.
6. Review the Terraform plan.
7. Confirm cleanup procedures.
8. Deploy only after explicitly authorizing resource creation.

### Deployment Documentation

[Deployment & State Management](docs/DEPLOYMENT.md)

[Plan Review](docs/PLAN_REVIEW.md)

[Costs & Cleanup](docs/COSTS_AND_CLEANUP.md)

---

# 🔍 5. Security Control Framework

The portfolio demonstrates several categories of security controls.

| Control Domain | Security Objective | Representative Implementation |
|---|---|---|
| Network Segmentation | Restrict unauthorized network movement | VPC routing and Transit Gateway controls |
| Traffic Inspection | Evaluate designated network traffic | AWS Network Firewall |
| Access Management | Reduce excessive privileges | IAM boundaries and explicit denies |
| Administrative Security | Protect sensitive access | MFA and restricted emergency roles |
| Audit Logging | Support investigation | AWS CloudTrail |
| Threat Detection | Identify suspicious activity | GuardDuty and Security Hub |
| Event Processing | Route and process findings | EventBridge and Lambda |
| Application Authentication | Validate API identities | Amazon Cognito |
| API Protection | Reduce unauthorized or abusive requests | AWS WAF and API Gateway |
| Data Protection | Restrict and recover stored data | DynamoDB permissions and PITR |
| Reliability | Handle processing failures | Retry and failure destinations |

These controls reflect the repository's intended and implemented design.

Actual runtime effectiveness requires the corresponding live verification.

---

# 🛠️ 6. Troubleshooting & Operational Support

Cloud security engineering includes identifying configuration problems, investigating failures, and restoring expected behavior.

The portfolio includes operational documentation and investigation patterns relevant to cloud support and security engineering.

| Issue | Investigation Focus | Potential Corrective Action |
|---|---|---|
| Network connectivity failure | Routes, firewall, NAT, security groups | Correct the affected network control |
| Unauthorized network access | Route propagation, network policies | Restrict unintended connectivity |
| IAM AccessDenied | Policies, boundaries, trust relationships | Correct authorized permission scope |
| Missing security findings | EventBridge, Lambda, OpenSearch | Restore event delivery or processing |
| Lambda execution failure | Logs, input, IAM, dependencies | Correct handler or environment issue |
| API authentication failure | Cognito, API Gateway, WAF | Correct identity or request configuration |
| DynamoDB conditional-write failure | Keys, conditions, idempotency | Validate request and data consistency |
| Terraform provider failure | Plugin execution, permissions, locks | Repair environment and rerun validation |

### Incident Investigation Method

```text
Identify the Symptom
        |
        v
Determine Scope and Impact
        |
        v
Collect Logs and Configuration Evidence
        |
        v
Identify the Failed Component
        |
        v
Evaluate Root Cause
        |
        v
Apply Controlled Remediation
        |
        v
Retest Expected Behavior
        |
        v
Document Findings and Prevention
```

This workflow represents a recommended operational approach, not a claim that every scenario has occurred during a live deployment.

---

# 📸 7. AWS Implementation Screenshots

The repository also preserves historical AWS Console screenshots from earlier hands-on activities.

**View the [AWS Screenshot Evidence Gallery](Images/README.md).**

The image collection covers:

| AWS Service | Historical Activity |
|---|---|
| Amazon VPC | Public subnet configuration |
| Amazon VPC | Web application security group |
| AWS IAM | EC2 application role |
| Amazon S3 | Bucket creation |
| Amazon API Gateway | POST method configuration |
| AWS Lambda | Python and DynamoDB integration |
| AWS Lambda / SQS | Event-source configuration |
| Amazon Athena | External table for S3 clickstream data |

These screenshots document earlier learning and implementation activities.

They are not presented as deployment evidence for the four current Terraform projects.

Current verification status is maintained separately in the repository's evidence and validation documentation.

---

# 📚 8. Engineering Documentation

The repository contains supporting technical documentation intended to make the projects reviewable, reproducible, and understandable.

| Document | Purpose |
|---|---|
| [START_HERE.md](START_HERE.md) | Reviewer and setup guidance |
| [Deployment Guide](docs/DEPLOYMENT.md) | Deployment prerequisites and state management |
| [Test Strategy](docs/TEST_STRATEGY.md) | Validation approach |
| [Evidence Methodology](docs/EVIDENCE.md) | Evidence standards |
| [Control Register](docs/CONTROL_REGISTER.csv) | Security control inventory |
| [Control Traceability](docs/CONTROL_TEST_TRACEABILITY.csv) | Control-to-test mapping |
| [Risk Register](docs/RISK_REGISTER.md) | Threats and risks |
| [Gap Analysis](docs/GAP_ANALYSIS.md) | Identified engineering gaps |
| [Architecture Decisions](docs/ARCHITECTURE_DECISIONS.md) | Design choices and tradeoffs |
| [Plan Review](docs/PLAN_REVIEW.md) | Infrastructure change review |
| [Release Readiness](docs/RELEASE_READINESS.md) | Deployment readiness |
| [Incident Tabletop](docs/INCIDENT_TABLETOP.md) | Security response exercises |
| [Costs and Cleanup](docs/COSTS_AND_CLEANUP.md) | Cost management and teardown |
| [Interview Guide](docs/INTERVIEW_GUIDE.md) | Technical project walkthrough |
| [Validation Report](reports/VALIDATION_REPORT.md) | Recorded test outcomes |
| [References](docs/REFERENCES.md) | Supporting technical references |

---

# 📁 9. Repository Structure

```text
aws-security-networking/
│
├── README.md
├── START_HERE.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── Makefile
│
├── projects/
│   ├── 01-network-core/
│   ├── 02-iam-guardrails/
│   ├── 03-security-logging-detection/
│   └── 04-secure-serverless-api/
│
├── docs/
│   ├── DEPLOYMENT.md
│   ├── TEST_STRATEGY.md
│   ├── EVIDENCE.md
│   ├── CONTROL_REGISTER.csv
│   ├── CONTROL_TEST_TRACEABILITY.csv
│   ├── RISK_REGISTER.md
│   ├── ARCHITECTURE_DECISIONS.md
│   └── ...
│
├── diagrams/
│   └── portfolio.svg
│
├── Images/
│   ├── README.md
│   └── Historical AWS screenshots
│
├── tests/
│   └── Offline security and functional tests
│
├── validation/
│   └── Validation resources
│
├── scripts/
│   └── Evidence and testing utilities
│
├── reports/
│   ├── VALIDATION_REPORT.md
│   └── Recorded validation artifacts
│
├── requirements-dev.txt
├── requirements-dev.lock.txt
│
└── .github/
    └── workflows/
        └── validate.yml
```

Each project maintains its own implementation and technical documentation.

Terraform `.tf.json` files use Terraform's supported JSON configuration format.

They are not AWS CloudFormation templates.

---

# 👨‍💻 10. Technical Skills & Professional Competencies

## AWS Cloud Infrastructure

Amazon VPC • Amazon EC2 • AWS Transit Gateway • AWS Network Firewall • NAT Gateway • Amazon S3 • AWS Lambda • Amazon DynamoDB • Amazon API Gateway

## Cloud Security

AWS IAM • Permission Boundaries • Least Privilege • MFA • Security Groups • AWS WAF • Amazon Cognito • AWS CloudTrail • Amazon GuardDuty • AWS Security Hub

## Security Operations

Threat Detection • Security Event Processing • Log Analysis • Incident Investigation • Failure Recovery • Risk Assessment • Security Control Validation

## Infrastructure & Automation

Terraform • Infrastructure as Code • Python • AWS SDK Concepts • Automated Testing • CI Workflows • Version Control • Technical Documentation

## Cloud Support & Troubleshooting

Network Diagnostics • IAM Troubleshooting • Application Error Analysis • Configuration Review • Root Cause Investigation • Operational Runbooks • Validation Reporting

---

# 🎯 11. Career Relevance

The portfolio is designed to communicate practical engineering skills relevant to several technical career paths.

| Target Role | Relevant Portfolio Experience |
|---|---|
| Cloud Support Engineer | AWS troubleshooting, networking, IAM, Lambda, logs |
| Cloud Engineer | Terraform, VPC architecture, infrastructure configuration |
| AWS Security Engineer | IAM controls, network protection, secure APIs |
| Cloud Security Analyst | Security findings, event processing, audit logging |
| Security Operations Analyst | Detection pipelines, investigation, response workflows |
| Infrastructure Support Analyst | Network diagnostics, configuration validation, runbooks |
| Junior DevSecOps Engineer | Infrastructure as Code, security tests, CI and validation |

### Technical Interview Discussion Topics

A reviewer can use the projects to explore questions such as:

- How do you isolate workloads inside AWS?
- How do permission boundaries differ from IAM policies?
- How would you investigate an AWS AccessDenied error?
- How can CloudTrail and GuardDuty support security investigations?
- How do you protect a serverless API?
- What happens when an SQS-triggered Lambda function fails?
- How do you validate Terraform infrastructure safely?
- How do you distinguish configuration evidence from verified deployment behavior?

The repository's [Interview Guide](docs/INTERVIEW_GUIDE.md) provides additional walkthrough material.

---

# 🚀 12. Recommended Next Validation Milestones

The remaining work should focus on verifying the implemented designs in an authorized environment.

| Priority | Milestone | Completion Evidence |
|---|---|---|
| P1 | Resolve Terraform provider execution | Successful provider-backed validation |
| P1 | Execute Terraform mock tests | Passing mock-test output |
| P1 | Confirm GitHub Actions CI | Successful workflow run |
| P2 | Review live Terraform plans | Reviewed, sanitized plan artifacts |
| P2 | Deploy projects in AWS sandbox | Successful deployment records |
| P2 | Execute 28 acceptance cases | Recorded results and logs |
| P2 | Verify negative security tests | Evidence of intended access denial |
| P3 | Exercise recovery and incident scenarios | Runbook execution evidence |
| P3 | Complete controlled teardown | Resource cleanup confirmation |

These milestones represent future validation activities, not completed accomplishments.

---

# 📌 13. Engineering Integrity & Project Scope

This repository is a personal technical portfolio laboratory developed to demonstrate cloud engineering, security architecture, troubleshooting, and implementation reasoning.

It is not presented as:

- A production customer deployment
- A commercial managed security platform
- An independently audited cloud environment
- A compliance-certified implementation
- Evidence of completed live AWS testing where such testing has not occurred

All security and deployment claims should be evaluated against the actual source code, recorded test outputs, and current validation status.

The purpose of the portfolio is to demonstrate technical capability through transparent, reviewable engineering work.

---

# 👤 14. About the Developer

**Jamie Christian II**

Cloud Engineering | Cloud Security | AWS Infrastructure | Technical Operations

Focused on designing, implementing, troubleshooting, and documenting secure cloud systems using AWS, Terraform, Python, and modern security engineering practices.

This portfolio reflects practical learning, engineering problem-solving, and an emphasis on building reliable, secure, and maintainable infrastructure.

**Professional Links**

- [GitHub Portfolio](https://github.com/JamieChristian22)
- [LinkedIn Profile](https://www.linkedin.com/in/jamiechristian2/)
- [AWS Security & Networking Repository](https://github.com/JamieChristian22/aws-security-networking)

---

**🛡️ AWS Security & Networking Portfolio**

*Building cloud security engineering skills through infrastructure design, implementation, automated validation, operational troubleshooting, and evidence-driven documentation.*
