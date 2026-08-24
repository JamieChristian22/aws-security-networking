# IAM Guardrail Validation

| Test | Expected |
|---|---|
| Create delegated role without required boundary | DENIED |
| Attach AdministratorAccess outside approved admin process | DENIED |
| ReadOnlyAuditor writes resource | DENIED |
| IncidentResponder reads GuardDuty/Security Hub | ALLOWED |
| Deployer performs approved deployment action | ALLOWED |
| Disable CloudTrail under protected SCP | DENIED |
| Leave AWS Organization | DENIED |
| Assume break-glass without MFA | DENIED |
| Assume break-glass with approved MFA context | ALLOWED + ALERTED |
