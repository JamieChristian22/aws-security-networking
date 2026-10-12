# Secure API architecture

Client → regional API Gateway REST API protected by WAF → Cognito authorizer → private Lambda → scoped DynamoDB gateway endpoint → encrypted table. Cognito accounts are administrator-provisioned and require software-token MFA. The API uses a public client with SRP authentication; no client secret is embedded in code.

## Control boundaries

| Boundary | Enforcement |
|---|---|
| Internet to API | WAF managed common rules and approximate per-IP rate limit |
| API to identity | Cognito user-pool authorizer validates the submitted ID token |
| API to Lambda | Function permission scoped to sandbox/POST/requests |
| Handler input | JSON-object shape, allowed fields, types, size, action values and key format |
| Handler to data | Runtime role can GetItem/PutItem only on its table; endpoint policy agrees |
| Data at rest | Customer-managed KMS encryption and DynamoDB PITR |
| Deletion | Table deletion protection and reviewed teardown |

Lambda subnets have no NAT or IGW route. Outbound TCP/443 is restricted to the DynamoDB managed prefix list, and the endpoint is associated with the private route table. The VPC execution managed policy provides ENI permissions; it is broader than the application data policy and is documented rather than described as perfectly minimal.

## Application consistency

The table key hashes the authenticated Cognito subject and idempotency key. A conditional PutItem makes the first successful request atomic. If a conflict occurs, a strongly consistent GetItem checks the stored owner and payload digest. Identical replay returns 200; changed content under the same key returns 409. Different subjects cannot collide by choosing the same key.

Only create-record behavior is implemented. `action` is stored metadata from a small allowlist; the API does not perform an actual customer update. No GET route, cross-tenant data query or arbitrary object mutation is exposed. Future routes must enforce owner authorization independently of customer labels.

## Logging and recovery

API access logs contain request ID, status, method, resource and latency, without payloads or tokens. Execution data tracing is disabled. WAF logs redact Authorization and Idempotency-Key and request sampling is disabled. Application logs record generic outcomes and request IDs. Do not add full events to logs during debugging.

PITR restores into a new table; restoring a backup is not automatic application failover. A controlled recovery includes table restore, policy/endpoint adjustment, configuration cutover and regression validation. The lab does not claim a measured RTO.
