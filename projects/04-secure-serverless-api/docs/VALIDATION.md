# Acceptance procedure

Run offline tests and provider validation first, then deploy only to the authorized sandbox. Follow the project deployment guide and runbook for prerequisites. The [acceptance ledger](../evidence/ACCEPTANCE.csv) is initially **NOT_RUN** because no live AWS execution occurred during this build.

| ID | Scenario | Expected |
|---|---|---|
| API-01 | Missing/expired/wrong-pool token | 401/403; no new item |
| API-02 | Valid authenticated request | 201 and one owner-scoped record |
| API-03 | Exact replay | 200 and unchanged item count |
| API-04 | Changed payload same key | 409 |
| API-05 | Malformed fields/types | 400 |
| API-06 | WAF managed-rule match | 403 block for reviewed synthetic input |
| API-07 | Controlled rate test | WAF block or gateway throttle as appropriate |
| API-08 | PITR restore and cutover drill | Restored data reconciles and app tests pass |

## Recording results

For each row, record actual output, UTC time, source revision, region/account, evidence file and reviewer. A negative test needs a known-working positive control where applicable. Mark inconclusive results as BLOCKED or FAIL with a reason; never infer PASS from the presence of a resource. Keep original captures private and publish sanitized copies.

## Exit criteria

All applicable rows must have reviewed evidence; nonapplicable controls require a documented scope decision. Include delivery/notification and recovery where relevant. An offline test or Terraform mock plan does not replace these live checks. Read the repository [evidence standard](../../../docs/EVIDENCE.md) for status definitions.
