# Runbook – Network Core

## Common tasks

### 1) New spoke VPC onboarding
- Create new VPC + subnets in workload account
- Attach VPC to TGW
- Associate/propagate routes using the correct TGW route tables
- Confirm `0.0.0.0/0` points to inspection

### 2) Troubleshoot "no internet" from a spoke
Checklist:
1. Spoke subnet route table has `0.0.0.0/0` → TGW
2. TGW attachment is available
3. TGW route table for spoke has default route → inspection attachment
4. Inspection VPC has subnets with Network Firewall endpoints
5. Network Firewall policy allows the traffic
6. NAT gateway is healthy; route from inspection to NAT is correct
7. Check logs:
   - VPC Flow Logs: rejected traffic?
   - Network Firewall logs: drop action?

### 3) Add a new allow rule
- Edit Terraform stateful rule group
- `terraform plan` and check for intended changes
- Apply, then validate with test traffic and logs

## Metrics to watch
- Network Firewall: dropped packets, allowed packets
- NAT: bytes processed, error port allocation
- TGW: bytes in/out (unexpected spikes)

## Incident response quick steps
- Identify affected spoke VPC/subnet
- Pull NFW logs for 15–60 minutes
- Compare with VPC Flow Logs to confirm path
- If exfil suspected: tighten rules (deny by default), rotate compromised credentials, isolate workload
