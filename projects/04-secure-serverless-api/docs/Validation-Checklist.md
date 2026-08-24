# Serverless Security Validation

1. Protected endpoint without token → 401/403.
2. Valid Cognito token → allowed.
3. Expired/invalid token → denied.
4. Oversized/invalid payload → 400.
5. WAF test pattern → blocked.
6. Burst above throttle → 429/rate control.
7. Lambda cannot access unrelated DynamoDB table.
8. DynamoDB encryption configured.
9. Alarm triggers on repeated Lambda errors.
10. CloudTrail records administrative changes.
