# Threat Model – Logging & Detection

## Threats
1. **Log tampering**
   - Mitigation: CloudTrail log file validation; S3 versioning + blocked public access; restrict bucket policy.
2. **Blind spots**
   - Mitigation: multi-region CloudTrail; GuardDuty + Security Hub enabled; event-driven routing.
3. **Excessive access to logs**
   - Mitigation: least-privilege IAM roles for investigation and ingestion.
4. **Sensitive findings exposed**
   - Mitigation: OpenSearch encryption at rest + node-to-node; restrict domain access with IAM and (recommended) VPC access.

## Residual risk
- This single-account deployment is a portfolio baseline. In enterprise, centralize into a dedicated security account with org-wide aggregation.
