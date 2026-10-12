# Network threat model

**Assets:** workload isolation, egress policy, routing integrity and investigation logs. **Trust boundaries:** spoke-to-TGW, TGW-to-inspection, inspection-to-internet and operator-to-control-plane.

| Threat | Abuse path | Mitigation | Test / residual risk |
|---|---|---|---|
| Lateral movement | Compromised dev workload reaches prod | Spoke-prefix blackholes and no propagation | Test a listening prod endpoint; other connectivity must be inventoried |
| Inspection bypass | Operator adds direct spoke egress or wrong endpoint route | Explicit route architecture and regression checks | Drift detection after apply still required |
| Unapproved protocol | Workload sends arbitrary egress | Strict-order firewall with TCP/443 allow | Positive 443 and negative alternative-port test |
| TLS exfiltration | Attacker uses allowed 443 destination | Logs provide visibility | Not prevented by port allow alone; domain/proxy control is future work |
| DNS tunnel | Workload uses VPC resolver | No specialized DNS control here | Documented residual risk; do not claim DNS inspection |
| Evidence loss | Logs disabled or removed | Logging resources and operational checks | Central tamper-resistant archive is a production extension |

Assume the provisioning administrator is trusted. This stack does not stop an unrestricted administrator from changing routes. No IPv6 is provisioned; future IPv6 requires equivalent routing and inspection review rather than inheriting IPv4 assumptions.
