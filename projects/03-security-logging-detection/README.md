# Private security logging and detection

CloudTrail captures management events, GuardDuty and Security Hub provide findings, and EventBridge feeds a private signed ingestion pipeline. Raw finding versions are archived before normalized documents are indexed. Failure paths have bounded retries and separate queues.

![Architecture](../../diagrams/03-security-logging-detection.svg)

## Review and run

- [Architecture and boundaries](docs/ARCHITECTURE.md)
- [Deployment prerequisites and commands](docs/DEPLOYMENT.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Operational runbook](docs/RUNBOOK.md)
- [Acceptance procedure](docs/VALIDATION.md)
- [Live evidence ledger](evidence/ACCEPTANCE.csv)
- [Canonical Terraform root](iac/terraform/)

Start with the repository [deployment guide](../../docs/DEPLOYMENT.md). This project has no claimed live AWS validation in the delivered package. See the [release report](../../reports/VALIDATION_REPORT.md) for executed checks and limitations.

## Definition of done

Provider validation and mock plans pass; an account-specific plan is reviewed; an authorized sandbox deployment succeeds; the listed positive and negative controls have actual evidence; alert delivery and cleanup are verified. A diagram or simulated expected result does not satisfy these gates.
