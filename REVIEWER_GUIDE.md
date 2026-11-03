# Reviewer guide and asset provenance checklist

**Project:** aws-security-networking · [README](README.md) · [License](LICENSE) · [CI runs](https://github.com/JamieChristian22/aws-security-networking/actions)

## Five-minute review

1. Read the root README for purpose, limitations, and simulated versus measured results.
2. Open the project paths below to inspect tracked deliverables; their presence alone is not proof of correctness.
3. Review GitHub Actions for actual test outcomes. Queued or failed runs are not passing tests.
4. Verify input datasets, calculation methods, and evidence before citing performance outcomes.

### Project entry points

1. [diagrams](<diagrams>)
2. [projects](<projects>)
3. [reports](<reports>)
4. [validation](<validation>)

## Third-party asset and dataset provenance checklist

The following are **sample tracked candidates** for source and reuse-rights checks. Their inclusion does not imply they are external, unlicensed, or unsafe.

| Tracked asset candidate | Verification status |
| --- | --- |
| `Images/API_Gateway_POST_Method_Creation_POC-API.png` | **Not independently verified** — check origin and permissions |
| `Images/AWS_Lambda_Python_Code_DynamoDB_PutItem_POC-Lambda-1.png` | **Not independently verified** — check origin and permissions |
| `Images/AWS_Lambda_SQS_Trigger_Configuration_POC-Lambda-1.png` | **Not independently verified** — check origin and permissions |
| `Images/Amazon_Athena_External_Table_Creation_S3_Clickstream.png` | **Not independently verified** — check origin and permissions |
| `Images/IAM_Role_EC2AppRole_Created.png` | **Not independently verified** — check origin and permissions |
| `Images/S3_Bucket_Creation_Success.png` | **Not independently verified** — check origin and permissions |
| `Images/VPC_Public_Subnet_Configuration.png` | **Not independently verified** — check origin and permissions |
| `Images/VPC_SecurityGroup_WebAppSG.png` | **Not independently verified** — check origin and permissions |

For each external asset, record original source URL, creator/provider, terms, allowed redistribution and commercial use, and any required notices. For original or synthetic work, note how it was produced and ensure any modeled results are plainly labeled. The MIT repository license does not automatically grant rights to externally owned content.

**Security:** Never include API keys, private/customer data, or identifying screenshots in an evidence file. Treat current-branch scanning and historical secret scanning as separate checks.

This document is **navigation and review guidance**, not a security audit pass, ownership certification, or legal clearance. See [GitHub Actions](https://github.com/JamieChristian22/aws-security-networking/actions) for live test results.
