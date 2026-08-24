# Detection Catalog

| Detection | Source | Severity | Response |
|---|---|---|---|
| GuardDuty HIGH/CRITICAL | GuardDuty/Security Hub | SEV-1/2 | security triage |
| CloudTrail stopped | CloudTrail event | SEV-1 | restore logging + investigate |
| Root account activity | CloudTrail | SEV-1 | validate legitimacy |
| IAM policy change | CloudTrail | SEV-2 | review principal/change |
| Security group opened to world | Config/Event | SEV-2 | validate/restrict |
| Break-glass role used | CloudTrail | SEV-1/2 | mandatory review |
