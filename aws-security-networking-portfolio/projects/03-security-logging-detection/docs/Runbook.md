# Runbook – Logging & Detection

## Daily operations
- Review HIGH/CRITICAL findings in Security Hub
- Use OpenSearch Dashboards for quick triage searches
- Track trends: top finding types, affected resources, accounts

## Investigation steps
1. Open Security Hub finding → note resource + timestamps
2. Search CloudTrail logs around the time window (CloudWatch Logs Insights)
3. Confirm principal identity, source IP, and API calls
4. Contain: disable access keys, isolate instances, apply SCPs (org), patch vulnerable resources
5. Document outcome and close finding

## Service health checks
- CloudTrail: logging enabled
- GuardDuty: detector enabled
- EventBridge: rule invocation metrics
- Lambda: error rate, throttles
- OpenSearch: cluster status green/yellow, free storage
