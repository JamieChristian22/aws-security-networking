# Validation Checklist – Network Core

## Routing
- [ ] Dev VPC subnets have `0.0.0.0/0` route to TGW
- [ ] Prod VPC subnets have `0.0.0.0/0` route to TGW
- [ ] Shared VPC subnets have `0.0.0.0/0` route to TGW
- [ ] TGW spoke RT has `0.0.0.0/0` to inspection attachment
- [ ] Hub RT contains routes back to spoke CIDRs

## Inspection
- [ ] Network Firewall endpoints are created in inspection subnets
- [ ] Stateful rule group enforces: deny non-HTTPS egress by default
- [ ] Domain allowlist/denylist is applied (if enabled)

## Logging
- [ ] Flow logs delivered to CloudWatch Logs
- [ ] Firewall alert/flow logs delivered to CloudWatch Logs
- [ ] Log retention is set (not infinite)

## Security
- [ ] Spokes have no IGW
- [ ] Spokes have no NAT gateway
- [ ] Only inspection VPC has NAT + IGW
