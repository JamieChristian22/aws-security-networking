# Acceptance procedure

Run offline tests and provider validation first, then deploy only to the authorized sandbox. Follow the project deployment guide and runbook for prerequisites. The [acceptance ledger](../evidence/ACCEPTANCE.csv) is initially **NOT_RUN** because no live AWS execution occurred during this build.

| ID | Scenario | Expected |
|---|---|---|
| NET-01 | HTTPS egress from each AZ | Allowed through expected firewall/NAT path |
| NET-02 | Dev to listening prod endpoint | Denied by explicit TGW segmentation |
| NET-03 | Egress to prohibited port | Denied while HTTPS positive control succeeds |
| NET-04 | Inspection return route | Same-AZ firewall traversed on return |
| NET-05 | Flow/firewall log delivery | Fresh records in configured groups |
| NET-06 | Controlled AZ-path failure | No uninspected bypass; recovery behavior recorded |

## Recording results

For each row, record actual output, UTC time, source revision, region/account, evidence file and reviewer. A negative test needs a known-working positive control where applicable. Mark inconclusive results as BLOCKED or FAIL with a reason; never infer PASS from the presence of a resource. Keep original captures private and publish sanitized copies.

## Exit criteria

All applicable rows must have reviewed evidence; nonapplicable controls require a documented scope decision. Include delivery/notification and recovery where relevant. An offline test or Terraform mock plan does not replace these live checks. Read the repository [evidence standard](../../../docs/EVIDENCE.md) for status definitions.
