# Failure Mode Analysis

| Failure | Impact | Response |
|---|---|---|
| Cognito issue | authentication unavailable | monitor AWS status, fail securely |
| Lambda errors | API 5xx | rollback/fix |
| DynamoDB throttle | elevated latency/errors | capacity/on-demand review |
| WAF false positive | legitimate traffic blocked | review sampled request/rule |
| key-policy error | encryption access failure | validate KMS grants |
