# Threat Model – IAM Guardrails

## Threats
1. **Privilege escalation (create policy version, attach admin policies)**
   - Mitigation: permission boundary prevents `iam:*` writes unless explicitly allowed; alarm on risky IAM APIs.
2. **Break-glass misuse**
   - Mitigation: MFA requirement in trust policy; CloudTrail + alarm for role assumption; short session duration; rotate secrets.
3. **Excessive standing access**
   - Mitigation: roles with least privilege; no long-lived access keys recommended; use SSO where possible.
4. **Undetected IAM drift**
   - Mitigation: CloudTrail to immutable storage; periodic Access Analyzer checks (recommended).

## Residual risk
- A compromised administrator with full account access can still bypass controls. In production, enforce SCPs at the org level and use separate security accounts.
