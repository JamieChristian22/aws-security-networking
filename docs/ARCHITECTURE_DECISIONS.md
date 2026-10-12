# Architecture decision records

## ADR-001: explicit segmented egress

**Context:** Development and production must not communicate, but both need controlled internet egress. **Decision:** disable TGW default association/propagation; use explicit spoke and inspection route tables, default inspected egress and spoke-prefix blackholes. **Alternative:** full mesh route propagation is simpler but makes unintended east-west connectivity easier. **Consequence:** shared-services VPC is isolated too. A future shared-service exception needs a narrow prefix/port design, a return path and negative tests; the current name does not imply shared access.

## ADR-002: dedicated inspection subnets and AZ affinity

**Decision:** each AZ has a TGW attachment subnet, a firewall endpoint subnet and a NAT subnet. Endpoint routes use the endpoint's reported AZ rather than the position of an unordered set. TGW appliance mode keeps stateful flows on the correct inspection path. **Tradeoff:** two NAT gateways and two firewall endpoints increase idle cost. **Rejected shortcut:** sharing the TGW and firewall subnet hides the steering boundary and makes the path difficult to verify. Failure remains closed; an outage is not repaired by routing around inspection.

## ADR-003: narrow routine roles, separate emergency trust

**Decision:** explicit existing operator role ARNs can assume routine roles. Their permissions boundary allows only the intended read/deployment envelope and denies IAM mutations. A separate emergency role trusts explicitly named MFA-enabled IAM users. **Tradeoff:** federated SSO MFA does not populate the IAM `aws:MultiFactorAuthPresent` key in the same way as direct IAM MFA; the emergency trust is deliberately limited and documented. **Limitation:** the read-only incident responder investigates but cannot quarantine workloads without an approved containment role.

## ADR-004: versioned findings rather than mutable latest-state documents

**Decision:** archive each finding version to S3 and use a document ID derived from product ARN, finding ID and normalized update timestamp. **Benefit:** retrying the same delivery is idempotent, and a delayed older event cannot overwrite a later version. **Tradeoff:** monthly indices contain multiple versions. A latest-state view must group by finding identity and select the greatest timestamp. This lab does not ship an automatic index-retention policy; the operator must review storage growth.

## ADR-005: private search, service-role authorization

**Decision:** OpenSearch has private VPC endpoints, TLS, node-to-node encryption, encrypted disks and an ingress rule from the ingestion security group only. The domain policy grants only the ingestion role's document-write operation. **Tradeoff:** there is no immediately browsable public dashboard or bundled analyst reader. Add a reviewed analyst role, private access path and search permissions before interactive investigations. Never reopen the domain to the internet for convenience.

## ADR-006: authenticated idempotent writes

**Decision:** API Gateway validates Cognito tokens, Lambda validates the request, and DynamoDB conditionally creates a subject-scoped request record. A replay with identical content returns 200; changed content under the same key returns 409. **Tradeoff:** stored idempotency records persist; this lab has no time-based expiry. Retention and deletion must be agreed before storing personal or regulated data. The customer identifier is metadata, not a cross-tenant authorization grant.

## ADR-007: independent roots and transparent evidence

**Decision:** four state boundaries, one canonical implementation each, pinned providers, no automatic deployment in CI and no fabricated live evidence. **Tradeoff:** independent IAM and detection labs can create duplicate management-event trails if both are deployed. Review cost and ownership, or consolidate a shared audit stack before broader adoption. Assertions on configuration are useful regressions but cannot prove AWS runtime enforcement.
