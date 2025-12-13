# Runbook – IAM Guardrails

## Routine operations
- Review CloudTrail alerts weekly
- Audit role permissions quarterly
- Validate permission boundary is applied to newly created developer roles

## Break-glass workflow
1. Incident commander approves use
2. Operator authenticates with MFA and assumes `BreakGlassAdminRole`
3. Perform minimal required actions
4. Exit role, document actions
5. Post-incident: review CloudTrail + tighten controls

## Alert response
When an IAM-risk alert triggers:
- Identify principal (user/role), source IP, and API call
- Confirm change intent (ticket/approval)
- If suspicious: disable credentials / detach policies / rotate keys, and start IR playbook
