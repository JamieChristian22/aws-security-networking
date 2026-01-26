# Validation Checklist – IAM Guardrails

- [ ] CloudTrail is enabled and writing to S3
- [ ] CloudWatch log group receives CloudTrail events
- [ ] SNS email subscription confirmed
- [ ] Alarm triggers on risky IAM action (test in sandbox)
- [ ] Permission boundary exists and is attachable
- [ ] BreakGlass role trust requires MFA
- [ ] ReadOnlyAuditorRole can list/describe but cannot create/delete resources
