# Acceptance procedure

Run offline tests and provider validation first, then deploy only to the authorized sandbox. Follow the project deployment guide and runbook for prerequisites. The [acceptance ledger](../evidence/ACCEPTANCE.csv) is initially **NOT_RUN** because no live AWS execution occurred during this build.

| ID | Scenario | Expected |
|---|---|---|
| DET-01 | Valid synthetic finding handler invoke | Archived and indexed |
| DET-02 | Exact fixture replay | Same version/document key |
| DET-03 | Index dependency failure | Exception then retry/failure destination |
| DET-04 | EventBridge target delivery failure | Delivery queue captures event |
| DET-05 | Matching high active new finding | SNS notification received |
| DET-06 | Unauthorized private search caller | No authorized data-plane access |
| DET-07 | CloudTrail management event | Delivered to audit stores |

## Recording results

For each row, record actual output, UTC time, source revision, region/account, evidence file and reviewer. A negative test needs a known-working positive control where applicable. Mark inconclusive results as BLOCKED or FAIL with a reason; never infer PASS from the presence of a resource. Keep original captures private and publish sanitized copies.

## Exit criteria

All applicable rows must have reviewed evidence; nonapplicable controls require a documented scope decision. Include delivery/notification and recovery where relevant. An offline test or Terraform mock plan does not replace these live checks. Read the repository [evidence standard](../../../docs/EVIDENCE.md) for status definitions.
