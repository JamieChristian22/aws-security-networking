# Cost model and controlled cleanup

## Estimate before deployment

No dollar amounts are claimed as current prices. Use the AWS Pricing Calculator for the selected region and save the dated estimate with assumptions. All projects are billable; network and detection resources continue charging while idle.

| Stack | Fixed / hourly drivers | Usage drivers | Cost decisions |
|---|---|---|---|
| Network | Two NAT gateways, Network Firewall endpoints, TGW attachments | NAT/TGW/firewall processing, flow-log ingestion, internet transfer | Short supervised window; do not remove one AZ and continue claiming equivalent resilience |
| IAM | Primarily audit/notification services | CloudTrail copies, logs, S3, SNS | Avoid duplicate account trails when combining projects |
| Detection | Two OpenSearch nodes and EBS | Findings, CloudTrail, GuardDuty, Security Hub, logs and S3 | Size volumes and retention; enabling Security Hub standards additionally needs Config design |
| API | WAF rules/ACL, KMS key | API calls, Lambda, DynamoDB requests/PITR, logs and notifications | Gateway endpoint has no hourly interface-endpoint charge; confirm all regional pricing |

Monthly modeled cost = sum(hourly resource rate × active hours × quantity) + processing GB × rate + request units × rate + storage GB-month × rate. Avoid counting NAT/firewall discounts or included processing twice; validate the current region's pricing terms. Include retained resources after teardown in the estimate.

Set a sandbox budget notification before the lab. A budget alert is delayed visibility, not a spending cap. Record an owner and a teardown time; do not rely on this repository to schedule deletion.

## Teardown sequence

1. Stop test traffic and capture needed evidence; confirm no investigation/legal retention hold.
2. From the correct canonical root and state, run `terraform plan -destroy -out=destroy.tfplan` and inspect every deletion.
3. **API:** DynamoDB deletion protection intentionally blocks deletion. If data is disposable and authorized for removal, change protection to false, review/apply that change, take any required backup, then review a new destroy plan. Do not delete state to bypass protection.
4. **IAM/detection:** versioned S3 buckets have `force_destroy=false`. Archive required evidence and explicitly delete all approved disposable object versions/delete markers, or retain the buckets under a documented owner and state migration. Terraform destroy will not silently purge them.
5. **SCP:** detach the sandbox policy through the same controlled configuration/state. Verify the management-account rollback path before changes.
6. **OpenSearch:** export any required findings before destroy; snapshots and retention must be reviewed. Do not delete a shared service-linked role that other domains require.
7. Review and execute the final saved destroy plan. Investigate partial failures and rerun plan; never assume the final console line proves all cost is gone.
8. Inventory NAT gateways, EIPs, firewall endpoints, TGW attachments, OpenSearch domains, log groups, buckets, queues and KMS keys. Check the next billing update.

KMS key deletion uses a 30-day pending-deletion window for the API key. Do not schedule deletion while retained encrypted data is still needed. Destroying account-level API Gateway logging settings can affect other APIs; only manage this singleton when the sandbox owns it.

## Recovery objectives

This lab does not claim measured RTO/RPO. Set objectives before drills and measure them. DynamoDB PITR provides a restore capability, not a proven recovery time. For findings, S3 versions are the durable replay source; OpenSearch can be rebuilt, but restore throughput, index mappings and freshness must be measured.
