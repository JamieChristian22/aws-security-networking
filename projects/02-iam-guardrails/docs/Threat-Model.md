# Threat Model

| Threat | Control |
|---|---|
| developer grants self admin | permission boundary + SCP |
| IAM policy version escalation | monitoring + bounded actions |
| disable audit trail | SCP deny |
| public S3 exposure | organization guardrail |
| stolen admin credentials | federation/MFA + short sessions |
| emergency role abuse | MFA + alerts + post-use review |
