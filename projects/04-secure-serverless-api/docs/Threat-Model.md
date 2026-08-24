# Threat Model

| Threat | Control |
|---|---|
| credential stuffing | Cognito controls + WAF/rate limits |
| injection/malformed payload | strict request validation |
| excessive API usage | API throttles + WAF rate rules |
| Lambda overprivilege | scoped execution role |
| data exposure | DynamoDB encryption + IAM |
| secret leakage | Secrets Manager/parameters, not code |
| destructive API calls | authorization + logging |
| outage | serverless managed scaling + alarms |
