# Tabletop: suspected credential misuse and attempted exfiltration

**Scenario:** a high-severity finding arrives for a sandbox identity, followed by an unexpected role assumption and a burst of outbound connections. All timestamps and examples below are an exercise plan, not an executed incident.

## Roles

| Role | Responsibility |
|---|---|
| Incident lead | Sets severity, scope and change approval; maintains timeline |
| Investigator | Uses read-only role to correlate CloudTrail, findings and flow logs |
| Containment operator | Uses a separately authorized role for isolation changes |
| Evidence custodian | Preserves original captures and redacted copies with checksums |
| Service owner | Confirms legitimate activity and accepts recovery |

## Exercise sequence

1. **Alert validity:** identify finding ID, product, account, region, resource and update time. Confirm this is not the synthetic fixture. Check for duplicate versions and suppressed/resolved findings before escalating.
2. **Identity scope:** locate AssumeRole and the source principal. Correlate session time, API calls and role policy changes. Do not assume an MFA-authenticated action is legitimate.
3. **Network scope:** identify source ENI/VPC and destination/port. Compare against application ownership and expected TLS endpoints. Remember the lab permits any destination on TCP 443 and does not inspect resolver DNS.
4. **Containment decision:** record why isolation is proportionate. Remove a reviewed route/SG permission or quarantine the affected workload through an authorized operator. Avoid deleting the resource or logs. The read-only incident role cannot perform this action itself.
5. **Evidence preservation:** capture original findings from S3, relevant CloudTrail results and configuration. Record UTC timestamps and hashes. Restrict raw evidence; do not paste tokens, secret values or complete customer data into an issue.
6. **Recovery:** rotate/revoke the compromised access path, review role trust and boundary changes, redeploy known-good infrastructure, rerun positive and negative tests and verify audit delivery.
7. **Closure:** service owner verifies functionality, incident lead verifies scope, and evidence custodian checks the timeline. Record root cause, detection gaps and follow-up tasks with owners and dates.

## Injects and expected decisions

| Inject | Good response |
|---|---|
| SNS email was never confirmed | Mark alert delivery failed; configure and test subscription before closing |
| OpenSearch returns errors | Use private S3 evidence and DLQ metrics; do not open the domain publicly |
| A denied network test times out | Validate a working positive control and route/log evidence before crediting a firewall block |
| Emergency role cannot be assumed through SSO | Recognize the IAM-user MFA trust limitation; use documented emergency identity, not a broad trust-policy workaround |
| Terraform destroy fails on data protection | Preserve the protection until explicit data-retention and deletion decisions are made |

## Post-incident deliverable

Write a one-page incident report with impact, timeline, root cause, containment, recovery evidence and lessons. Mark measured durations separately from target durations. Never invent an MTTR or a blocked-attack count from this exercise plan.
