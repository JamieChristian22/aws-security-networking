# Migration from the previous repository

Baseline repository: https://github.com/JamieChristian22/aws-security-networking

Baseline revision: `6bac950d66ca1411bd664aa0ed891835d0468109`.

## What changed structurally

The previous `iac/terraform/main.tf` fragments and `iac/terraform/envs/dev` roots were independent configurations. This package replaces both with one canonical root per project using supported `.tf.json` syntax. The old network modules were superseded by an explicit route topology. The API has one handler (`handler.py`); detection has one handler (`ingest_securityhub.py`). Old simulated pass sheets were replaced with unexecuted acceptance ledgers.

## Source-only replacement

1. Preserve the current repository in a branch or archive.
2. Extract this package into a new directory and run the local checks.
3. Compare the full trees, including deletions. Do not copy only added files over the original.
4. Keep your Git history and remote; replace source content with the reviewed package in a feature branch.
5. Review the diff and run CI before merging. No GitHub commit or push was made while producing this ZIP.

## If the old Terraform was ever applied

Do not apply this package against old state blindly. Resource addresses and design have changed. First inventory the deployed resources, back up state and record the old root used to create each resource. Choose either a fresh isolated sandbox deployment or a reviewed migration with explicit moved/import blocks and one resource owner. Terraform can otherwise plan destructive replacement or duplicate resources.

This ZIP intentionally does not include guessed state migrations. It cannot know which version, if any, was deployed in your account. Keep the original configuration available until old resources are safely retired.

## Historical images

The Images directory is preserved from upstream for provenance. It is not current deployment evidence. Remove any images containing sensitive identifiers before publishing; retain useful sanitized examples only when their captions accurately describe what they show.

## Evidence upgrade: handler compatibility

API request identifiers retain the previous subject-plus-key SHA-256 scheme, so existing idempotency rows remain addressable. Strict parsing now rejects duplicate JSON fields, ambiguous headers and invalid UTF-8; clients must send one unambiguous JSON object. A conditional-write conflict whose stored row cannot be read returns retryable 503 instead of misleading 409.

Finding document identifiers now hash an unambiguous tuple of product ARN, account ID, finding ID and UTC-normalized update time. Existing v1 search documents retain their old identifiers. Replaying old archives into the same indices can therefore create duplicate logical findings. Before upgrading a previously deployed lab, choose a fresh domain/index generation or a reviewed reindex-and-deduplication migration; retain the raw S3 archive and reconcile counts before retiring old indices. Do not treat retries across this version boundary as deduplicated.
