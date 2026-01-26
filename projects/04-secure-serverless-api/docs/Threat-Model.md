# Threat Model – Secure Serverless API

## Threats & mitigations
1. **Unauthenticated access**
   - Mitigation: Cognito authorizer required on all methods.
2. **Abuse / DDoS / brute force**
   - Mitigation: WAF rate-based rule + managed rule group; API throttling.
3. **Data exposure**
   - Mitigation: HTTPS enforced; KMS encryption for secrets; least-privilege IAM.
4. **Public egress from compute**
   - Mitigation: Lambda runs in private subnets; uses VPC endpoints for AWS APIs.
5. **Silent failures**
   - Mitigation: CloudWatch alarms to SNS on error/throttle spikes.

## Residual risk
- Add custom WAF rules and bot control for advanced threats; enable Shield Advanced for high-risk APIs.
