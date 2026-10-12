# Acceptance procedure

Run offline tests and provider validation first, then deploy only to the authorized sandbox. Follow the project deployment guide and runbook for prerequisites. The [acceptance ledger](../evidence/ACCEPTANCE.csv) is initially **NOT_RUN** because no live AWS execution occurred during this build.

| ID | Scenario | Expected |
|---|---|---|
| IAM-01 | Auditor read inventory | Allowed |
| IAM-02 | Auditor bucket creation permission | Denied |
| IAM-03 | Deployer changes unrelated Lambda | Denied |
| IAM-04 | Break-glass without MFA | STS denies assumption |
| IAM-05 | Approved MFA break-glass | STS succeeds and alert received |
| IAM-06 | CloudTrail delivery | Fresh validated management events |
| IAM-07 | Optional SCP enforcement | Protected actions denied when attached |

## Recording results

For each row, record actual output, UTC time, source revision, region/account, evidence file and reviewer. A negative test needs a known-working positive control where applicable. Mark inconclusive results as BLOCKED or FAIL with a reason; never infer PASS from the presence of a resource. Keep original captures private and publish sanitized copies.

## Exit criteria

All applicable rows must have reviewed evidence; nonapplicable controls require a documented scope decision. Include delivery/notification and recovery where relevant. An offline test or Terraform mock plan does not replace these live checks. Read the repository [evidence standard](../../../docs/EVIDENCE.md) for status definitions.
