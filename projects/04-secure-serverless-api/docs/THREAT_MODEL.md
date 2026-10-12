# API threat model

**Assets:** authenticated user context, request records, idempotency integrity, encryption keys and availability. **Boundaries:** public client, gateway authorizer, function event, data endpoint and administration.

| Threat | Control | Residual risk / test |
|---|---|---|
| Unauthenticated write | Cognito authorizer and handler subject check | Live missing/expired/wrong-pool token tests |
| User chooses another owner's identity | Owner comes from verified subject | No read/update route is implemented; future routes need ownership checks |
| Malformed JSON causes errors | Strict object/type/field validation | Offline negative corpus and live representative case |
| Duplicate request creates duplicate data | Conditional write and subject-scoped key | Offline replay/conflict; live concurrent test future extension |
| Burst or malicious request | WAF, throttling, size bounds and concurrency cap | Approximate rate enforcement and workload baselines |
| Function accesses unrelated tables | Table ARN and endpoint principal/resource restriction | Live or simulated deny case |
| Sensitive request leakage | No body/token logs; redacted WAF headers | Operator debugging changes require review |
| Data deleted accidentally | PITR and deletion protection | Actual restore and cutover evidence still required |

No frontend security review, OAuth scope model, customer-system authorization, PCI/HIPAA certification or penetration-test result is implied by the backend controls.
