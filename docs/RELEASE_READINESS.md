# Release readiness and evidence review

## Acceptance gates

| Gate | Pass criteria | Current evidence |
|---|---|---|
| Package integrity | All manifest files match and ZIP integrity succeeds | Executed during packaging |
| Application behavior | Full suite passes; handler coverage remains 100%; selected mutations detected | Executed offline; reports contain raw results |
| Infrastructure source consistency | Resource references, protection relationships and handler wiring checks pass | Executed offline; no provider evaluation implied |
| Provider compatibility | All four roots initialize, validate and pass mock plans | BLOCKED locally; not yet demonstrated |
| Actual plan review | Real account plan reviewed with selected automated rules and human sign-off | NOT_RUN; synthetic checker tests only |
| Live security and recovery | All 28 acceptance cases have actual outcomes and evidence | NOT_RUN |
| Publication | Source branch and CI uploaded with repository write permission | GitHub returned 403; no branch or commit created |

## Evidence package a reviewer should receive

Keep the exact source revision or manifest, runtime/dependency snapshot, command transcript, timestamps, exit codes and the acceptance ledger together. A screenshot without a command, identity context or expected result is weak evidence. Prefer machine-readable output plus a short explanation of what it proves. Redact account identifiers where necessary, tokens, customer data and secrets before sharing. Keep unredacted evidence in an access-controlled location. Historical images in this package are not current deployment proof.

`docs/CONTROL_TEST_TRACEABILITY.csv` maps every live control to relevant offline selectors and states the remaining limitation. Some operational controls have no offline behavioral proof; those rows say so explicitly. Presence of a source assertion does not upgrade a live status.

## Change and recovery discipline

Before deployment, record purpose, affected roots, expected resource changes, spend limit, approved account/region, responsible operator and rollback decision. Review the plan for replacements and state ownership. A Git revert is not an infrastructure rollback: data and resource replacement may be irreversible without a tested backup.

For API failure, preserve table data and inspect gateway, Lambda and DynamoDB evidence before retrying. Verify idempotency after recovery; do not delete records to force a success response. For detection failure, preserve archived findings and failure queues, repair the dependency, then replay a bounded sample before a full recovery. Version changes to document identity require the migration procedure. For network failure, inspect forward and return routes and AZ mappings before changing default routes; never introduce an uninspected shortcut to make a test pass. For IAM lockout, use only the separately approved emergency access path and retain audit evidence.

A rollback decision should state its trigger, the last known usable configuration, the data reconciliation method and the validation to run afterward. If recovery requires new destructive actions, obtain separate approval. Do not disable controls merely to make a deployment complete.

## Interpreting the results

100% handler coverage measures executed Python statements and branches, not all possible inputs or service configurations. Eight detected mutations describe eight selected defects, not a universal score. SDK emulation tests real application-to-SDK calls while replacing AWS service behavior. Static source checks can identify broken references and missing relationships without proving Terraform schema correctness. The plan checker applies selected rules to structured input, not AWS authorization semantics.

These distinctions make the package reviewable without inflating its readiness. Portfolio depth and deployability should be judged separately. Successful provider CI and live acceptance are still necessary before claiming fully verified infrastructure.

## Finishing the blocked CI gate

The user approved a separate validation branch. The connected GitHub integration returned HTTP 403 for tree creation, so no source upload, branch creation or workflow execution succeeded. An authorized repository maintainer can import this full source tree into a feature branch and push it using their own normal GitHub access, or restore the connection's write access. Keep `main` unchanged until checks and review pass. The included workflow uses no AWS credentials and contains no apply command.
