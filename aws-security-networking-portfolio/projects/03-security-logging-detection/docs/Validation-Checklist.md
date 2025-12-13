# Validation Checklist – Logging & Detection

- [ ] CloudTrail is logging and delivering to S3
- [ ] CloudTrail events visible in CloudWatch Logs group
- [ ] GuardDuty detector enabled
- [ ] Security Hub enabled and standards enabled
- [ ] EventBridge rule triggers on Security Hub findings
- [ ] SNS email subscription confirmed
- [ ] OpenSearch domain is reachable (via endpoint)
- [ ] Lambda writes findings to OpenSearch index
