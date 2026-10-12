# API deployment and first request

## Regional prerequisite

API Gateway account-level CloudWatch role configuration is shared across APIs in a region. Leave `manage_api_gateway_account=false` when centrally managed, and verify a working role is configured. In a disposable account that owns the setting, set it true. The stage has access logs and method logging enabled; missing regional logging permissions can prevent creation.

Review KMS/table protection and costs before apply. Confirm the plan creates the Lambda from `lambda/handler.py`, supplies TABLE_NAME, creates the DynamoDB endpoint route and binds the Cognito authorizer to POST.

## Cognito user enrollment

Self-signup is disabled. An administrator creates a synthetic test user using the AWS console or `AdminCreateUser`, then the client completes password replacement and TOTP enrollment. The app client supports SRP and refresh-token flows. Use an SRP-capable Cognito client, such as an existing test application built with the AWS-supported authentication SDK flow; this repository is the backend and does not include a login frontend.

A first login can return NEW_PASSWORD_REQUIRED and MFA_SETUP. Complete the new-password challenge, associate a software token, verify its TOTP, respond to MFA_SETUP, and complete subsequent SOFTWARE_TOKEN_MFA challenges as requested. Never commit the TOTP seed or password. Capture only the challenge names/statuses in evidence.

After a successful login, keep the **ID token** in a local process environment named API_ID_TOKEN. Token lifetime is 15 minutes. Do not paste tokens into an issue, screenshot or shell command saved in history. A token from another pool must fail authorization.

## Low-volume acceptance

From the repository root with boto3 needed only for the evidence collector:

```bash
python scripts/test_api_live.py --url "$API_URL" --execute-sandbox-writes
```

The script sends five synthetic requests: unauthenticated, initial create, exact replay, changed-content conflict and invalid type. It prints status codes and expectations only; it does not print tokens. It creates one synthetic record. The explicit flag is required because this is a live write test.

This script does not test expired tokens, MFA enrollment, WAF signatures, quota behavior or PITR recovery. Run those separately using the acceptance ledger. The delivered offline tests do not claim that Cognito itself was tested.

## Teardown

Export required evidence and review data retention. Table deletion protection must be deliberately disabled and applied before an approved destroy. Preserve data keys while retained data needs them. Do not remove shared regional API Gateway configuration without its owner's approval.
