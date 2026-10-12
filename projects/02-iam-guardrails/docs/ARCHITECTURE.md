# IAM policy architecture

## Role model

| Role | Trust | Permission envelope | Deliberate limitation |
|---|---|---|---|
| Auditor | Explicit existing operator role ARNs | Inventory, security findings, CloudTrail lookup and log reads | No resource mutation or S3 object reads |
| Responder | Same explicit operator trust | Investigation reads | No quarantine/delete actions; containment is separately authorized |
| Deployer | Same explicit operator trust | Get/update code/configuration of `name-workload-*` Lambda functions | No CreateFunction, IAM mutation or PassRole |
| Break-glass | Explicit existing IAM user ARNs with MFA age <= 3600 seconds | AdministratorAccess, maximum one-hour role session | Not bounded by the routine boundary; still subject to applicable SCPs |

Role names use the configured prefix. The boundary allows the read envelope and narrowly named Lambda changes, then explicitly denies IAM mutations and selected security-service changes. An identity policy must still grant an action. A boundary alone does not grant permission.

## Evaluation examples

- Auditor EC2 describe: the identity policy and boundary both allow it; other applicable policies can still deny it.
- Auditor bucket creation: neither the identity policy nor the boundary permits it.
- Deployer updates an unrelated Lambda: the resource ARN does not match the allowed prefix.
- A routine role receives an accidental admin policy: the boundary continues to constrain identity-policy permissions, including its explicit IAM deny.
- A resource policy grants access directly to a session principal: evaluate this separately. IAM resource-policy/session semantics are not fully captured by a simple intersection diagram.

## Trust and emergency controls

The operator must already have permission to call STS AssumeRole and must match an allowed principal. Break-glass trust intentionally uses IAM user MFA context. It is not a ready-made IAM Identity Center emergency workflow. MFA device enrollment, custody, approval and emergency-access reviews are operating procedures, not Terraform-enforced human approvals.

CloudTrail writes validated multi-region management events to private versioned S3 and a CloudWatch log group. Metric filters cover risky IAM changes and emergency role assumptions. SNS email is optional and must be confirmed. S3 uses explicit SSE-S3, not a customer-managed KMS key; the documentation does not claim otherwise.

## Optional SCP

With an empty target ID, no SCP is created or attached. With a reviewed sandbox target, the policy denies stopping/deleting trails, deleting GuardDuty detectors, disabling Security Hub and leaving the organization. It does not enforce every boundary-creation requirement or replace all organization governance. SCPs do not grant permissions and do not constrain management-account principals in the same way as member-account principals. Keep a management-account rollback procedure.
