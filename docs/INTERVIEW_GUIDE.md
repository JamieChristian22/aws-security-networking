# Interview walkthrough

## 60-second introduction

“I built four AWS sandbox projects covering network segmentation, IAM guardrails, security detection and an authenticated serverless API. I focused on connecting the implementation to its security claims: complete forward and return firewall routes, permission boundaries that allow intended work, private signed finding ingestion and an API with user-scoped idempotency. I added regression tests and documented the live acceptance evidence still required. The current release has executed offline checks; I do not present it as a production deployment.”

## Demonstration path

Show the diagram, one important Terraform resource, a failing-condition test, and the corresponding operational runbook. A clear end-to-end path is more useful than reading a list of AWS services.

| Question | Technical answer to demonstrate |
|---|---|
| Why can dev not reach prod? | Spoke TGW table has explicit more-specific blackholes for spoke CIDRs; propagation is disabled. Show how that route wins over the default inspected egress route. |
| Does creating Network Firewall inspect traffic automatically? | No. Explain TGW subnet → same-AZ firewall endpoint → NAT and the return NAT-subnet route back to the firewall. |
| Why appliance mode? | Preserve flow affinity for stateful inspection across the TGW attachment. Do not claim that this alone fixes all asymmetric route designs. |
| Does a boundary grant permissions? | No. Intended identity-based permissions need an allow in both the role policy and boundary; explicit denies still win. Resource-based policies and session principals require separate analysis. |
| Can the incident responder quarantine a server? | The shipped role is read-only. Containment requires a separate approved role; explain that boundary rather than pretending it has administrator powers. |
| Why not public OpenSearch? | Findings are sensitive. Private networking, TLS and SigV4 narrow access. An analyst reader path is an explicit later design decision. |
| What happens if indexing fails? | Archive first, raise the error, bounded retry, then processing DLQ. Replayed finding versions use stable IDs. |
| What does idempotency protect? | Retries do not create duplicate records; key + authenticated subject determines identity. Same key with changed content returns 409. |
| Is WAF a complete security solution? | No. Authentication, input validation, least privilege, rate controls and monitoring remain separate layers. |
| How do you prove a deny? | Pair the negative test with a functioning positive control and source/destination evidence. A timeout alone is inconclusive. |

## Honest resume phrasing

Use “developed and tested AWS security reference implementations” while live deployment remains unverified. After actual deployment, describe only the controls and outcomes you personally validated. Do not claim enterprise customer impact, compliance certification, attack volumes or percentage improvements without real evidence.

## Practice exercise

Spend five minutes explaining one packet's round trip, five explaining one IAM allowed and denied request, five tracing one failed finding delivery, and five demonstrating API replay/conflict behavior. End by naming one residual risk and the next evidence gate for each project.
