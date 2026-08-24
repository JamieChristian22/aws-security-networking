# Secure API Runbook

## Authentication Failure Spike
Check Cognito metrics, API authorizer failures, WAF activity, and client release changes. Confirm no credential-stuffing pattern.

## Lambda Error Spike
Check logs, recent deployments, downstream DynamoDB errors, throttles, and permissions. Roll back if deployment-correlated.

## Suspected Data Exposure
Restrict affected role/API path, preserve logs, review CloudTrail and access patterns, identify records exposed, rotate secrets/tokens if relevant, and complete incident review.
