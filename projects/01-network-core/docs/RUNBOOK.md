# Network operations runbook

## Symptom: allowed HTTPS cannot reach the destination

**Owner:** network operator. **First response:** verify whether one workload, one AZ or all spokes are affected. Record UTC time, source IP/ENI, destination, port and DNS result. Keep the original route snapshot before changing anything.

1. Confirm the destination is listening and the same request succeeds from a known-good source.
2. Inspect the source subnet route-table association. A route on an unassociated table has no effect.
3. Inspect the TGW attachment state and its associated route table; verify the default route points to inspection.
4. Compare inspection TGW-subnet route targets with the firewall endpoint reported for that AZ.
5. Check firewall sync state and policy, then the firewall-subnet NAT route and the NAT-subnet return routes.
6. Check NAT availability, port-allocation errors and IGW attachment. Verify source security group and NACL return-port handling.
7. Correlate flow logs with firewall alert/flow logs. A VPC ACCEPT record does not prove the firewall permitted the end-to-end request.

Useful reads:

```bash
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPC_ID"
aws ec2 get-transit-gateway-route-table-associations --transit-gateway-route-table-id "$TGW_RT_ID"
aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id "$TGW_RT_ID" --filters Name=state,Values=active,blackhole
aws network-firewall describe-firewall --firewall-arn "$FIREWALL_ARN"
aws network-firewall describe-logging-configuration --firewall-arn "$FIREWALL_ARN"
```

## Symptom: dev reaches prod

Treat this as a segmentation incident. Preserve route and attachment association snapshots. Confirm the traffic did not use a different peering/VPN/proxy path. Inspect for removed blackholes, unintended propagation and changed spoke associations. Restore the reviewed route configuration through Terraform, with a saved plan and approval. Re-test the denied path and a valid internet path before closure.

## Symptom: an AZ path fails

Identify the failed endpoint, NAT or subnet route. Preserve failure evidence. Do not route around the firewall. Verify service health and inspect the alternate-AZ path with a new test connection. Escalate if failover requirements exceed the lab design. Recovery requires firewall-ready state, consistent route tables and repeated positive/negative checks in both AZs.

## Closure evidence

Keep incident timeline, before/after route snapshots, Terraform change reference, firewall/flow-log correlation, positive/negative results and the service owner's acknowledgment. Record measured recovery duration rather than assuming an RTO from the architecture diagram.
