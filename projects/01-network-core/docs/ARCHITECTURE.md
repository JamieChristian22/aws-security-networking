# Network architecture and packet walkthrough

## Address plan

| VPC | CIDR | AZ A workload subnet | AZ B workload subnet |
|---|---|---|---|
| Inspection | 10.0.0.0/16 | See dedicated tiers below | See dedicated tiers below |
| Development | 10.10.0.0/16 | 10.10.0.0/24 | 10.10.1.0/24 |
| Production | 10.20.0.0/16 | 10.20.0.0/24 | 10.20.1.0/24 |
| Shared | 10.30.0.0/16 | 10.30.0.0/24 | 10.30.1.0/24 |

Inspection tiers: TGW 10.0.0.0/24 and 10.0.1.0/24; firewall 10.0.2.0/24 and 10.0.3.0/24; NAT 10.0.4.0/24 and 10.0.5.0/24. Subnets do not auto-assign public IPs. The NAT subnets have an IGW route, but no user workload is placed there.

## Route contracts

| Route table | Destination | Target | Purpose |
|---|---|---|---|
| Spoke VPC | 0.0.0.0/0 | TGW | No direct egress |
| TGW spokes | Each spoke /16 | Blackhole | Explicit cross-spoke isolation |
| TGW spokes | 0.0.0.0/0 | Inspection attachment | Inspect internet-bound traffic |
| Inspection TGW subnet, per AZ | 0.0.0.0/0 | Firewall endpoint in that AZ | First-hop steering |
| Firewall subnet, per AZ | 0.0.0.0/0 | NAT in that AZ | Translate inspected internet traffic |
| Firewall subnet, per AZ | Each spoke /16 | TGW | Return toward workload |
| NAT subnet, per AZ | 0.0.0.0/0 | IGW | Internet edge |
| NAT subnet, per AZ | Each spoke /16 | Firewall endpoint in that AZ | Inspect return traffic |
| TGW inspection | Each spoke /16 | Matching spoke attachment | Return delivery |

The automatically created VPC local route remains. There are no implicit TGW route propagations. More-specific spoke blackholes take precedence over the default route. The shared VPC is also isolated; adding access to a shared service requires a deliberate design change.

## HTTPS round trip

1. A development instance resolves a destination using the VPC resolver; the resolver path is not inspected by this firewall.
2. Its private subnet default route targets TGW. TGW's spoke table chooses the inspection attachment for a public destination.
3. The inspection attachment subnet routes to the firewall endpoint matching that subnet's AZ.
4. The strict-order policy permits TCP traffic to destination port 443 and drops other unmatched traffic. This is a port policy, not TLS decryption or hostname validation.
5. The firewall subnet sends the allowed packet to the same-AZ NAT. NAT translates the source, and the NAT subnet sends it to the IGW.
6. The response returns to NAT. After reverse translation, the spoke-specific route on the NAT subnet sends it through the same-AZ firewall.
7. The firewall subnet's spoke route sends it to TGW. The inspection TGW table selects the original spoke attachment.

Appliance mode is enabled on the inspection attachment. Endpoint IDs are selected by reported AZ; Terraform must not assume an unordered endpoint set maps to the caller's list order.

## Observability and failure behavior

All VPCs emit flow logs. Network Firewall emits flow and alert logs. NAT port-allocation errors have alarms. This is not a complete production observability pack: endpoint health dashboards and workload-specific latency/error SLOs need real traffic baselines.

A firewall/AZ outage must not be “fixed” by inserting an uninspected default route. Existing sessions can break; test the remaining-AZ path with new sessions and record observed behavior. No automatic cross-AZ failover or availability percentage is claimed. Network ACLs remain the default and are not presented as an additional deny layer.
