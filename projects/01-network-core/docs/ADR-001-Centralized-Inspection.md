# ADR-001 — Centralized Inspection

**Decision:** Route spoke internet egress through a shared Inspection VPC and AWS Network Firewall.

**Rationale:** Centralizes policy, logging, and egress governance.

**Tradeoff:** Adds TGW/firewall/NAT processing cost and routing complexity.

**Revisit trigger:** Very high data-processing cost or workload-specific latency requirements justify distributed inspection.
