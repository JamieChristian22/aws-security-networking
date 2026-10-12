# Upgrade changelog

## Infrastructure review and release readiness upgrade

- Added a local Terraform plan-risk checker with 30 synthetic negative and positive tests.
- Added nine resource-graph, S3 protection and Lambda wiring checks.
- Added a 28-control offline/live traceability matrix and detailed plan/release review procedures.
- Re-executed the full 186-test suite and preserved the distinction between offline and live evidence.
- Recorded the authorized GitHub upload attempt and HTTP 403 access failure.

## Execution-evidence upgrade

- Hardened API parsing, Unicode handling, identity validation and ambiguous replay failures.
- Scoped finding identity by account, normalized timestamps and validated complete batches before writes.
- Added real SigV4 construction with destination validation and disabled proxy/redirect forwarding.
- Added network-blocked SDK emulation, deterministic property tests and eight targeted mutation checks.
- Executed 147 tests with 100% handler statement/branch coverage and zero Bandit findings.
- Added a repeatable evidence runner, dependency snapshot and raw machine-readable reports.
- Prepared credential-free CI; repository upload was blocked by automatic approval review pending explicit authorization. No GitHub or AWS changes occurred.

## Complete source upgrade

- Consolidated four projects into one canonical Terraform root each.
- Rebuilt symmetric inspected network routing and explicit spoke isolation.
- Corrected boundary permissions, role trust and CloudTrail destination policies.
- Replaced public OpenSearch with private signed ingestion and failure queues.
- Connected Cognito/WAF/Lambda/DynamoDB with input validation and subject-scoped idempotency.
- Added behavior regressions, structural control tests, provider mock tests and credential-free CI.
- Added five architecture figures, detailed operational guides, risk/control registers, migration guidance and 28 live acceptance cases.
- Replaced simulated passing results with explicit NOT_RUN live statuses.

See reports/VALIDATION_REPORT.md for executed results and remaining verification gates. This package did not modify GitHub or deploy AWS resources.
