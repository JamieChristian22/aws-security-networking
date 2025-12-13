# Validation Checklist – Secure Serverless API

- [ ] Cognito user pool created
- [ ] API Gateway uses Cognito authorizer
- [ ] Unauthenticated request returns 401
- [ ] Authenticated request returns 200
- [ ] WAF Web ACL attached and blocks/rate limits as expected
- [ ] Lambda logs written
- [ ] VPC endpoints exist (logs, sts, kms)
- [ ] Alarms created and SNS subscription confirmed
