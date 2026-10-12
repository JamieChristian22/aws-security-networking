# IAM threat model

**Assets:** temporary credentials, role trust, boundaries, audit history and organization membership. **Trust boundaries:** operator-to-STS, role-to-resource, account-to-organization and audit delivery.

| Threat | Control | Residual risk / test |
|---|---|---|
| Overbroad attached policy | Boundary allow envelope plus explicit IAM deny | Simulate privilege escalation and test approved reads |
| Untrusted principal assumes a role | Explicit principal lists | Test one allowed and one nontrusted identity in sandbox |
| Stolen routine session changes audit controls | Boundary does not permit those mutations | Session theft still permits allowed reads until expiry |
| Emergency role misuse | Named IAM users, MFA age, short session and alert | Human approval/custody is not automatically enforced |
| Boundary removal | Routine roles cannot mutate IAM | Provisioning/admin roles remain a separate trust boundary |
| Audit disabling in member account | Optional SCP | Disabled by default; no organization control claim until attached and tested |
| Sensitive logs accessed by investigator | Read scope and account isolation | Log content must be governed; do not log tokens/PII unnecessarily |

The scope is role-based lab governance, not a complete enterprise identity lifecycle. There is no automated joiner/mover/leaver system, Identity Center permission-set management, access-review service or resource-policy analyzer in this root.
