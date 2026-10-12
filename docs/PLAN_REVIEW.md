# Reviewing a deployment plan

## Purpose and stop conditions

`validation/review_plan.py` reviews selected security risks in an already generated Terraform plan. It reads a local JSON file, emits resource addresses and rule identifiers, and never calls AWS or Terraform. Its success status is deliberately `PASS_SELECTED_CHECKS`: this is not deployment approval.

The checker rejects invalid or unsupported input, an empty resource-change list, and malformed resource metadata. It flags deletions, replacements and state-forgetting actions. It requires known enabled public-access protections, CloudTrail logging/integrity settings, KMS rotation, DynamoDB deletion protection/PITR/encryption, and OpenSearch encryption/HTTPS settings. It also flags automatic subnet public addressing, unrestricted IPv4/IPv6 security-group ingress, missing API method authentication and optional/disabled Cognito MFA. Unknown selected security fields require review.

An empty plan is handled separately: inspect the Terraform exit code and summary to establish that no changes are proposed. Do not manufacture an empty resource list to satisfy this checker.

## Operator procedure

1. Verify the ZIP checksum manifest before changing files. Install pinned dependencies in a virtual environment and run `make evidence`.
2. Run provider-backed `make terraform-check` in an authorized environment. Resolve failures before generating an AWS plan.
3. Use the deployment guide to select the root, account, region, state backend and example variable file. Confirm identity with `aws sts get-caller-identity`. The account must match the configured allowlist.
4. From the chosen Terraform root, run `terraform plan -out=review.tfplan` with the reviewed variable arguments. Inspect its exit status; do not continue from a failed plan.
5. Run `terraform show -json review.tfplan > plan.local.json`. This export can contain plaintext secrets even when Terraform labels values sensitive. Keep both files local, access-restricted and out of Git.
6. From the repository root, run `python validation/review_plan.py /absolute/path/to/plan.local.json --output reports/local/plan-review.json`. Exit 0 means selected checks passed; exit 1 means review is required or the input could not be evaluated.
7. Read every flagged resource in the original plan. For an intentional destructive change, require a migration/backup/restore plan and separate approval. There is no automatic waiver switch. Record approved exceptions in the change record without modifying the checker to hide them.
8. Complete the human review below. Apply only the exact saved binary plan that was reviewed, in the same account, region, workspace and state context. A changed plan requires new review.
9. Capture acceptance evidence and verify cleanup. Remove private plan exports according to your evidence-retention policy.

## Human review remains mandatory

| Review area | Questions to resolve | Required evidence |
|---|---|---|
| Identity and trust | Which principals can assume roles? Does an identity policy plus boundary permit only intended actions? Are any resource-policy principals broader than expected? | Policy diff, trust evaluation and positive/negative sandbox tests |
| Packet paths | Are both directions routed through the intended firewall? Do route-table associations and AZ mapping agree? | Plan route inventory plus live flow/firewall observations |
| Data recovery | Does replacement affect existing tables, domains, buckets or encryption keys? Is restore tested? | Backup identifiers, restore drill and reconciliation results |
| Exposure | Are interfaces, API endpoints, IPv6 paths and standalone rules expected? | Endpoint inventory, rule review and unauthorized-caller tests |
| Operations | Do subscriptions, logs, DLQs and alarms actually receive events? Are concurrency and quotas sufficient? | Timestamped delivery/alert observations |
| Cost and cleanup | Which resources bill while idle? Can retention/protection settings prevent deletion? | Cost estimate, planned shutdown time and deletion checklist |

## Known limitations

The checker implements a selected rule set for this portfolio. It does not evaluate arbitrary IAM policy JSON, route reachability, network ACLs, all possible public CIDR ranges, organization policies, DNS, quotas, prices, provider schemas, data-source correctness or remote drift. Resource types without a specific security rule receive only generic destructive-action checks. A permitted rule could still be too broad for your requirements. Unknown values outside the selected fields are not comprehensively rejected.

Security-group world exposure detection checks the exact unrestricted CIDRs `0.0.0.0/0` and `::/0`; equivalent split ranges need human review. The tool does not analyze policy semantics or prove that encryption keys are usable. It does not print resource values, but resource addresses can still reveal internal naming. Review output before publication.

All 30 plan-checker tests use synthetic JSON. They prove that the checker responds to its fixtures; they are not evidence that a real portfolio plan has been generated successfully.
