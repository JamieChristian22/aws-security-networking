# IAM Security Runbook

## Break-Glass Use
1. Open incident/change record.
2. Obtain approver.
3. Authenticate with MFA.
4. Assume emergency role for shortest practical session.
5. Perform only incident-required action.
6. Preserve CloudTrail evidence.
7. End session.
8. Conduct mandatory post-use review.

## Suspected Privilege Escalation
Disable/contain affected principal, inspect CloudTrail, review policy versions/assume-role changes, remove persistence, rotate credentials where relevant, and document blast radius.
