# IAM deployment

1. Inventory existing trusted principals. Supply exact role ARNs in `trusted_principal_arns`; no account-root wildcard trust is used.
2. Supply exact IAM user ARNs with working MFA devices in `breakglass_principal_arns`. Ensure their identity policies permit the intended AssumeRole operation. Use a separate emergency-access test window.
3. Leave `scp_target_id` empty initially. Set `alert_email` to the intended notification address if using email; confirm the resulting subscription.
4. Validate, mock-test and review a real plan. CloudTrail delivery depends on a destination policy tied to the trail ARN.
5. Apply only to the sandbox, then check trail status and delivered objects. Service-side delivery can lag resource creation.

## Read-only permission simulation

Obtain actual role ARNs from `terraform output -json role_arns`.

```bash
aws iam simulate-principal-policy --policy-source-arn "$AUDITOR_ARN" --action-names ec2:DescribeInstances s3:CreateBucket
aws iam simulate-principal-policy --policy-source-arn "$DEPLOYER_ARN" --action-names lambda:UpdateFunctionCode --resource-arns "$APPROVED_FUNCTION_ARN" "$UNRELATED_FUNCTION_ARN"
```

Save complete simulator output including missing context. Simulation does not fully establish SCP, trust-policy, cross-account or service-specific enforcement. Pair it with safe real read/assume-role checks. Do not attempt a destructive action on a shared trail to manufacture a deny screenshot.

## Emergency access test

Use the authorized IAM user session and the actual MFA device ARN. Supply the time-based token only through a secure local prompt; never record it in transcripts or Git. An approved STS AssumeRole call should return temporary credentials, which must be handled privately. Verify the CloudTrail event, metric and received alert; sign out and revoke test sessions where appropriate.

## Optional organization rollout

Test policy JSON with IAM Access Analyzer using the appropriate policy type before attachment. Review a dedicated OU/account target and inventory applications that need protected service changes. A management-account administrator must own detach/rollback. This is an opt-in extension, not a prerequisite for the other IAM controls.
