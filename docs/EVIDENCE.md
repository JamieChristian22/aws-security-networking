# Evidence standard and acceptance process

## Status vocabulary

| Status | Meaning |
|---|---|
| PASS_OFFLINE | A named local test actually executed and passed |
| FAIL | An executed check did not meet its expected outcome |
| BLOCKED | The check could not execute because a documented prerequisite was unavailable |
| NOT_RUN | A planned check has not been attempted |
| PASS_LIVE | A live authorized check produced reviewed expected and actual evidence |

Do not substitute NOT_RUN with PASS because the architecture looks correct. A CloudWatch log-group screenshot proves existence, not delivery, retention enforcement or incident response. A Terraform plan proves intended actions, not successful resource creation.

## Evidence record

Each live test ledger includes a control ID, scenario, expected result, current status and evidence path. After running a test add UTC time, account/region, source commit, executor, exact command, exit status, actual result, raw capture checksum and reviewer. If retries are needed, keep the failed attempt and the corrected attempt. Avoid editing original captured logs to make a result look cleaner.

`python scripts/collect_evidence.py --help` documents a read-only collector. Install boto3 separately in the operator environment. It confirms account identity, captures only selected configuration/status responses, hashes them and reports per-call errors. It does not issue a control PASS. IAM identifiers and resource metadata are still sensitive; keep raw files private and publish only reviewed redacted copies with separate hashes.

## Evidence tiers

1. **Source:** exact commit/configuration and reviewed plan.
2. **Execution:** command transcript or SDK output from the actual sandbox.
3. **Outcome:** expected versus actual with positive and negative cases.
4. **Operations:** alarm delivery, owner acknowledgment and documented resolution.
5. **Recovery:** restore or rollback results with measured elapsed time.

Production claims need all relevant tiers. A mock provider only validates Terraform's planned configuration behavior without calling AWS. It cannot demonstrate service quotas, service-specific API restrictions, route convergence, MFA enrollment or alarm delivery.

## Safe sequence

Begin with configuration reads. Then use low-volume synthetic activity in isolated resources. Do not stop a real production trail, disable a detector, alter an organization root or inject unreviewed attack traffic to make a screenshot. Use IAM simulation for broad destructive-deny cases; a later live test must be designed so an unexpected allow cannot damage shared infrastructure.

For denied network tests, compare against a positive control from the same source. A timeout alone could mean DNS failure or a stopped workload. Collect routes, firewall logs and flow logs, and verify that the destination really was listening during the positive-control window.

## Integrity

The release manifest hashes delivered files. It detects accidental modification relative to that manifest; it is not a digital signature, identity attestation or proof that the content is secure. After modifying files, regenerate the manifest and retain the original release for comparison.
