# Detection threat model

**Assets:** finding evidence, audit history, notification availability and search confidentiality. **Boundaries:** service-to-event-bus, event-bus-to-function, function-to-private-store and operator-to-investigation interface.

| Threat | Implemented control | Residual risk / validation |
|---|---|---|
| Public finding disclosure | Private OpenSearch and private blocked-public S3 | Verify both resource policies and network path |
| Forged search writes | SigV4 and writer-role document scope | A compromised ingestion role can alter allowed documents |
| Replayed events | Deterministic version-specific IDs | S3 versioning may create extra object versions; lifecycle contains growth |
| Delayed old event overwrites current state | Append version identity | Analyst latest-state query must select correct version |
| Dependency error silently drops a finding | Exceptions, retries, archive-first order and processing DLQ | Monitor and replay before retention expires |
| Event delivery fails | Separate EventBridge delivery DLQ | Full alert-path coverage still needs live tests |
| Unbounded indexing/retention cost | Scoped patterns and operational review | No automatic index retention; lab must be time bounded |
| Audit administrator deletes evidence | Versioning and TLS-only delivery | Separate-account Object Lock design remains future work |

This is not a full SIEM product. No production detection efficacy, mean-time-to-detect, analyst staffing or compliance outcome is claimed.
