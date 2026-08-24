# 02 — IAM Zero-Trust Guardrails

A practical AWS identity-governance project combining **permission boundaries, least-privilege roles, break-glass access, SCP policy examples, CloudTrail visibility, risky-IAM-event monitoring, and validation matrices**.

## Security Objective
Prevent privilege escalation and accidental weakening of security controls while preserving a controlled emergency-administration path.

## Control Layers

```text
AWS Organizations SCP
        ↓
Permission Boundary
        ↓
IAM Role Policy
        ↓
Temporary Session
        ↓
AWS Resource
        ↓
CloudTrail / Alerts
```

## Core Roles
- ReadOnlyAuditorRole
- IncidentResponderRole
- DeployerRole
- BreakGlassAdminRole

## Key Guardrails
- deny disabling CloudTrail
- deny leaving the organization
- deny public S3 policy changes in protected OUs
- require approved permission boundary for delegated role creation
- require MFA context for break-glass assumption
- alert on break-glass use and risky IAM API changes
