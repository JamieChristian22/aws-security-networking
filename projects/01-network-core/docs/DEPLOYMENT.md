# Network deployment

Use `iac/terraform` only. Set account ID, name, region and two AZs. The CIDRs are fixed non-overlapping lab ranges; confirm they do not overlap existing connectivity before adding external attachments. There are no VPN, peering, Direct Connect or organization resources in this stack.

## Before apply

- Confirm quotas for VPCs, NAT gateways, elastic IPs, TGW attachments and Network Firewall.
- Price two-AZ resources and set a teardown time.
- Run the root checks, then review the account-specific plan. Expect three spoke VPCs plus inspection, four TGW VPC attachments, two NATs and a firewall with two endpoint mappings.
- Confirm no direct internet gateway was added to a spoke and no route propagations appeared.

## After apply

```bash
terraform output -json
aws network-firewall describe-firewall --firewall-arn "$FIREWALL_ARN"
aws ec2 describe-transit-gateways --transit-gateway-ids "$TGW_ID"
aws ec2 describe-transit-gateway-attachments --filters "Name=transit-gateway-id,Values=$TGW_ID"
```

Set these shell variables from the actual outputs; do not use example IDs. Wait for firewall readiness and in-sync policy before acceptance. Capture route-table associations as well as route contents.

## Test workload prerequisites

The stack deliberately creates no EC2 instances or paid permanent test agents. For packet tests, create temporary approved instances in selected spoke subnets with no public IP, an SSM-managed role and a security group that permits only the test flows. Arrange Session Manager through the allowed HTTPS egress or separately reviewed private endpoints. Do not open SSH to the internet.

Use an endpoint you own as a listening destination. Run one positive HTTPS check and one prohibited-port check from the same source; verify the listener separately. For cross-spoke tests, create a synthetic listener in the other spoke and allow the chosen test port in its security group so the TGW deny, rather than an unrelated SG deny, is the intended blocking layer.

Delete the temporary test instances and their volumes when finished. Their costs and state are separate from this Terraform root unless you explicitly manage them in another reviewed configuration.
