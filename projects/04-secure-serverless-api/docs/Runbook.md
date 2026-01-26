# Runbook – Secure Serverless API

## On-call checks
- API Gateway 5XX error rate
- Lambda errors and duration
- WAF blocked requests and rate limits

## Common issues
### 401 Unauthorized
- Verify client is sending Authorization header (Bearer token)
- Confirm token is from this user pool and not expired

### 5XX Errors
- Check Lambda logs for exceptions
- Confirm VPC endpoints are healthy and security group allows HTTPS to endpoints

## Security response
If abuse detected:
- Tighten WAF rate threshold
- Add IP set block rules
- Reduce API Gateway burst limits temporarily
