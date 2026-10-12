# Deployment and state management

## Scope and release gates

Each directory `projects/<name>/iac/terraform` is a separate root and state. There is no root `terraform apply` for all projects. The stacks intentionally avoid automatic organization-wide changes. Run only in an authorized sandbox after reviewing charges, service quotas, permissions and the destruction procedure.

| Gate | Required evidence | Stop condition |
|---|---|---|
| Offline | Passing Python tests and repository validator | Any failed assertion |
| Provider | Successful initialization, validation and mock test | Unsupported resource arguments or failed assertions |
| Plan | Saved plan reviewed against intended account, region and inventory | Replacement/deletion not understood; unexpected public access |
| Apply | Complete apply output and real resource identifiers | Partial failure; investigate before retry |
| Acceptance | Positive + negative control tests and sanitized raw evidence | A negative test succeeds or a required positive test fails |
| Teardown | Destroy plan, approved data handling and post-destroy inventory | Persistent billable resources or missing retained evidence |

## Prerequisites

- Terraform 1.9.8+ below 2.0 and pinned providers in each `.terraform.lock.hcl`.
- AWS CLI v2 with an SSO/session profile, not long-lived keys committed to files.
- A disposable commercial-region AWS account. The ingestion hostname check currently targets commercial-region OpenSearch, not GovCloud/China.
- Two available AZs in the selected region for network, detection and API projects.
- IAM permissions for only the services in the selected stack. Initial infrastructure provisioning needs broader permissions than runtime roles; do not give those provisioning permissions to Lambda.
- Approved resource naming, costs, and quotas. Account-level service owners must approve ownership of GuardDuty, Security Hub, API Gateway settings and service-linked roles.

## First run

From one canonical root:

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit account_id, region, names and any required trust ARNs before proceeding.
aws sts get-caller-identity
terraform init -input=false -lockfile=readonly
terraform validate
terraform test
terraform plan -out=reviewed.tfplan
terraform show -no-color reviewed.tfplan
# Execute only after reviewing the plan and accepting the sandbox cost.
terraform apply reviewed.tfplan
terraform output -json > outputs.local.json
```

`allowed_account_ids` prevents the AWS provider from operating in a different account than the explicit `account_id`. It does not verify that you own that account or that a change is appropriate. Keep plan files and output files private; they can contain infrastructure identifiers and sensitive values. Delete `outputs.local.json` before publishing or move it outside the repository.

Change `azs` whenever `aws_region` changes. Different accounts can map AZ names to different physical zones; this single-account lab does not assume cross-account AZ-name equivalence.

## State backend

Local state is supported for isolated learning, but it is sensitive and must not enter Git. For a shared workflow, provision a private versioned state bucket with encryption and a DynamoDB lock table separately. Restrict the state-reader role; protect the KMS key if used. Terraform 1.9.8 supports the S3 backend with DynamoDB locking used in this example.

Create `backend.tf` in the selected root containing:

```hcl
terraform {
  backend "s3" {}
}
```

Copy `backend.hcl.example` to a private file, enter the real bucket and lock-table name, then run `terraform init -migrate-state -backend-config=backend.hcl`. Inspect and back up existing state before confirming migration. The package deliberately does not create a state bucket using the same state it is meant to store.

## Existing services

- **GuardDuty / Security Hub:** only one account-level enablement per region. Set the create flags false to leave existing ownership untouched. Import only after reviewing the current configuration and state ownership.
- **OpenSearch service-linked role:** its name is account-scoped. Leave creation false when already present; set true only in a sandbox where you own its lifecycle.
- **API Gateway CloudWatch role:** a regional singleton. Leave `manage_api_gateway_account=false` if centrally managed, and ensure the existing role works. Set true only in a dedicated sandbox that owns the regional setting.
- **SCP:** leave `scp_target_id=""` on the first run. Attaching a deny policy can block even emergency administration in member accounts. Use a dedicated sandbox account or OU and retain a management-account rollback path.

## Runtime dependencies and credentials

The Python Lambdas use boto3/botocore supplied by the AWS Python runtime. This keeps the lab package small but allows SDK versions to change with runtime updates. Production promotion should package and pin those dependencies, scan them and rerun integration tests. The runtime roles use temporary credentials automatically; source code contains no AWS access keys.

Email subscriptions require a human confirmation after apply. An unconfirmed subscription means alarms may exist without reaching a person. Acceptance must include a real notification test.

## Promotion beyond a sandbox

Do not promote by changing an environment label alone. Required work includes separate account/state boundaries, organization logging delegation, service-control review, workload-specific egress allowlists, vulnerability/dependency scanning, capacity/load evidence, alert delivery ownership, backup restoration evidence and least-privilege deployment permissions. Record exceptions and approval dates. None of these gates are implied by a green unit-test run.
