# IAM operations runbook

## Legitimate action unexpectedly denied

Capture request action/resource, role session ARN, account/region and time; do not capture credentials. Inspect identity policy, permissions boundary, SCP, session policy, resource policy and endpoint policy. Verify trust separately from service permission. Use simulation to identify missing context, then compare with the real denied event. Do not attach AdministratorAccess as a general troubleshooting step.

If a boundary change is necessary, identify the exact required action/resource and whether it enables privilege escalation indirectly. Review the diff, simulate allowed and denied cases, apply to the sandbox and retest. Preserve the negative cases so broadening one permission does not silently authorize unrelated resources.

## Risky IAM-change alert

1. Locate the CloudTrail event and initiating session.
2. Compare to a change ticket and the expected provisioning role.
3. Inspect the changed trust/policy document and attached boundaries.
4. If unauthorized, escalate for containment and preserve the before/after policy versions.
5. Use a separately authorized operator to revoke compromised access; the shipped investigation role cannot mutate IAM.
6. Rerun allowed/denied simulations and confirm audit delivery before closure.

## Break-glass use

Acknowledge the alert immediately during a planned test or incident. Record approver, reason, principal and session start/expiry. Confirm MFA was enforced and review the complete subsequent API timeline. At closure, remove temporary elevation introduced during the incident, review credential/MFA custody, and record why routine roles were insufficient. The maximum session duration is not the same as immediate revocation.

## CloudTrail or notification delivery fails

```bash
aws cloudtrail get-trail-status --name "$TRAIL_NAME"
aws sns list-subscriptions-by-topic --topic-arn "$TOPIC_ARN"
aws logs describe-metric-filters --log-group-name "$TRAIL_LOG_GROUP"
```

Inspect `LatestDeliveryError` and CloudWatch delivery status. Check the bucket source-ARN restriction, object prefix and CloudWatch delivery-role permissions. Confirm the email subscription is not PendingConfirmation. Generate a safe read event and verify delivery, then exercise the intended alert without changing production security controls.

## SCP rollback

Stop additional organization changes. Use the predesignated management-account operator to detach the specific policy from the sandbox target. Record policy ID, target, reason and affected operations. Investigate before reattachment; never widen an organization policy simply to silence an unexplained AccessDenied.
