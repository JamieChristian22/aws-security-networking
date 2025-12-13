# Threat Model – Network Core

## Assets
- Spoke VPC workloads (Dev/Prod/Shared)
- Routing controls (TGW route tables)
- Egress inspection policy (Network Firewall)
- Logging (Flow Logs, Firewall logs)

## Trust boundaries
- Spokes → TGW (east/west boundary)
- TGW → Inspection VPC (control boundary)
- Inspection VPC → Internet (egress boundary)

## Threats & mitigations
1. **Unrestricted internet egress**
   - Mitigation: all default routes from spokes send `0.0.0.0/0` to inspection; egress via centralized NAT.
2. **Bypass inspection**
   - Mitigation: no IGW/NAT in spokes; only hub has NAT/IGW; spoke route tables do not provide direct egress.
3. **Lateral movement between spokes**
   - Mitigation: separate TGW route tables; only required routes propagated; optionally enforce with SG/NACL and AWS NFW in inspection.
4. **Misconfigured firewall rules**
   - Mitigation: versioned Terraform; explicit stateful rules; CloudWatch logs + alarms; peer review.
5. **Visibility gaps**
   - Mitigation: VPC Flow Logs + NFW logs to CloudWatch; retention configured.

## Residual risk
- If a spoke workload is compromised, it may attempt allowed egress (e.g., HTTPS). Enhance with DNS filtering, AWS Route 53 Resolver DNS Firewall, and per-workload egress allowlists.
