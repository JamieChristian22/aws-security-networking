# Test design and traceability

## Reproduce the offline result

Use Python 3.12 in a fresh virtual environment. Install `requirements-dev.lock.txt` for the exact observed dependency versions, then run `make evidence`. Direct dependency choices are in `requirements-dev.txt`; the lock is a version snapshot, not a hash-verified supply-chain lock. Review package changes before updating it. All checks record UTC start/end times, command arguments and exit codes in `reports/execution.json`. Handler, configuration and test hashes tie execution to source; the release manifest covers the packaged files.

The evidence runner executes tests, targeted mutation checks, Bandit and repository consistency checks. It continues after failures to collect diagnostics, but exits nonzero if any gate fails. It does not run Terraform or AWS deployments. `make terraform-check` is the separate provider-backed gate; the workflow also runs it on four isolated roots.

## Risk-to-test mapping

| Risk | Executed checks | Boundary of evidence |
|---|---|---|
| Authentication bypass or cross-user overwrite | Application tests, Moto DynamoDB lifecycle, authentication and tenant-scope mutations | Cognito token validation and API Gateway configuration require live acceptance |
| Duplicate requests and ambiguous network failure | Conditional-write/replay tests; actual boto3 writes with simulated lost response | Emulator cannot establish real consistency or concurrent regional behavior |
| Parser confusion and resource exhaustion | Duplicate keys/headers, malformed claims, UTF-8, nesting and body bounds | Upstream gateway size/rate enforcement remains unproven |
| Unexpected JSON values | Two deterministic Hypothesis properties, 300 examples each | 600 generated examples within two tests, not exhaustive input exploration |
| Archive loss or silent indexing failure | Moto S3 versioning/encryption, Stubber AccessDenied, failure/replay and mutation tests | No actual KMS, S3 event delivery or OpenSearch operation |
| Finding identity collision | Cross-account identity, timestamp normalization and account-scope mutation | Version-boundary migration requires explicit deduplication |
| Unsigned or redirected search request | Real botocore SigV4 headers/body assertions; bad destination, proxy and redirect rejection | No TLS handshake, DNS, IAM evaluation or OpenSearch authorization exercised |
| Missing infrastructure guardrail | Structural regression assertions and packaged Terraform mock tests | Only structural assertions executed; provider mock tests remain unrun |

## Isolation and meaningful failures

`tests/conftest.py` supplies synthetic credentials, disables metadata discovery and blocks socket construction. Moto emulates AWS in process; Stubber injects SDK failures; a captured request replaces HTTPS for signed-search tests. Passing tests cannot accidentally depend on a developer's AWS account.

The mutation harness first verifies that baseline selectors pass. It changes one behavior in a temporary source copy and requires pytest exit code 1: collection errors are not credited. All eight chosen regressions were detected. This is a targeted sensitivity check, not a comprehensive mutation score.

## Observed coverage and limits

186 tests passed. Coverage records 228 executable statements and 96 branches across the two deployed handlers, all exercised. Configuration files, AWS services, Terraform providers and operational runbooks are outside that coverage denominator. Coverage alone cannot demonstrate correctness, exhaustive edge cases or production readiness. Bandit reports no findings for the Python code under `projects`; it is not a dependency or infrastructure vulnerability audit.

The run emitted 33 botocore `datetime.utcnow()` deprecation warnings on Python 3.12. They are preserved in the transcript; they did not fail the checks. The SDK version should be upgraded through the same gates before the deprecated API becomes unavailable.

## Infrastructure review additions

Thirty synthetic plan-review tests exercise destructive changes, selected disabled or unknown protections, IPv4/IPv6 world ingress and malformed input. Nine source-graph tests check same-root resource references, per-bucket access-block relationships and deployed handler wiring. These checks supplement provider validation and live acceptance; they do not replace either.

## Gates still required

1. Approve uploading the prepared source/workflow to a validation branch, or run the included workflow in an independently authorized checkout. Authorization was subsequently granted, but GitHub returned HTTP 403 for tree creation. No branch was created.
2. Obtain successful provider-backed validate and mock-plan logs for all four roots. Local provider IPC restrictions prevented execution; do not translate this into a pass.
3. Review an actual plan and costs in an authorized disposable AWS account. Execute all 28 live acceptance cases, recording positive and negative outcomes, timestamps and evidence.
4. Resolve failed controls, verify cleanup and independently review evidence before making deployment-readiness claims.

Implementation confidence and testing evidence are therefore materially improved but cannot honestly be certified as 10/10 in this environment.
