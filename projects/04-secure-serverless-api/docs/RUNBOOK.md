# API operations runbook

## Authentication failures

Differentiate an API Gateway authorizer rejection from a WAF block using access/WAF logs and request IDs. Verify the token is an ID token from the expected pool and not expired; check the client flow and required MFA challenge completion. Do not log/decode a production token into a public ticket. If an identity was disabled, understand that issued JWT validation may continue until expiry; do not promise immediate revocation of every bearer token.

## HTTP 400 or 409

400 usually indicates the documented input contract was violated. Reproduce using synthetic data, inspect field types and header casing, and confirm the request's decoded size. Do not widen validation solely to accept malformed clients without a contract decision.

409 means a key was reused with different content. The client must not automatically generate a new key after an ambiguous timeout if that could duplicate a business operation. First retry the original payload/key; use a new key only for a confirmed distinct submission.

## HTTP 503 / storage errors

Check Lambda error logs without enabling payload tracing. Verify table name, DynamoDB endpoint association/policy, Lambda security-group prefix-list egress, KMS key state and role data permissions. Observe DynamoDB and Lambda throttles. Retry with the same idempotency key after backoff. Do not grant dynamodb:* on all tables as a shortcut.

## WAF false positive or abuse

Correlate request ID/time with WAF rule ID and gateway status. Use sanitized synthetic reproduction. If a managed-rule exception is necessary, narrow it to the relevant request scope, document expiration and rerun the malicious/benign pair. Do not disable the entire web ACL. Rate limits are approximate and not a hard per-user quota.

## Restore drill

1. Define the target recovery point and record the table ARN, key ARN and incident time.
2. Restore PITR to a new table in the authorized sandbox; do not overwrite the original.
3. Verify encryption, schema, item samples and expected data at that recovery point.
4. Review runtime role and endpoint permissions for the restored ARN and update TABLE_NAME through Terraform or an approved change.
5. Rerun create/replay/conflict checks and business reconciliation before cutover acceptance.
6. Record elapsed restore and validation time, data gap and rollback path. Retire old/restored test resources only after retention review.

## Closure

Require healthy synthetic transaction, negative auth/input test, confirmed alarms, sanitized before/after config and owner acknowledgment. A successful Lambda console test alone does not validate Cognito, WAF or API Gateway.
