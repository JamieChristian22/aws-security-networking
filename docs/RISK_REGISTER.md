# Threat and residual risk register

Ratings are qualitative engineering judgments for this sandbox, not audited enterprise risk scores.

| ID | Risk / threat | Implemented mitigation | Residual risk and required decision |
|---|---|---|---|
| R01 | Cross-environment movement | Explicit TGW spoke-prefix blackholes | No shared-service exception; test each future exception |
| R02 | Exfiltration over permitted TLS | Stateful 443 egress only, no direct route | Port 443 is not a destination/domain allowlist and does not decrypt TLS; add domain/proxy controls when required |
| R03 | DNS-based exfiltration | AWS resolver used for normal VPC DNS | Resolver traffic is not inspected by the egress firewall; DNS Firewall is future work |
| R04 | AZ or firewall outage | Two independent AZ paths and appliance mode | Existing sessions may drop; no untested automatic route-repair promise |
| R05 | IAM escalation | Boundary allow envelope plus IAM deny; explicit trust | Privileged provisioning role and emergency role remain powerful |
| R06 | Emergency account compromise | Named user trust, MFA age and short session | Requires MFA-device governance, custody, alert acknowledgment and periodic review |
| R07 | SCP lockout | Disabled by default; separate sandbox target | Management-account rollback ownership required before attachment |
| R08 | Audit tampering | Versioned private S3, TLS-only policy, CloudTrail validation | No Object Lock; privileged administrators can still delete; production archive should be separate account |
| R09 | Lost findings | S3-first writes, raised errors, bounded retries, two DLQs | Operators must monitor DLQs; retention is 14 days, not infinite |
| R10 | OpenSearch unauthorized access | VPC security group, role scope, SigV4 and encryption | No analyst workflow until a reviewed reader path is added |
| R11 | Search cluster degradation | Two AZ nodes and red-cluster alarm | Small lab topology is not an HA/SLA guarantee; yellow status and storage pressure need production alarms |
| R12 | Duplicate or out-of-order events | Deterministic version-specific IDs | Multiple versions need latest-state aggregation and retention management |
| R13 | Token theft | Cognito MFA, 15-minute tokens and no token logging | Issued JWTs can remain valid until expiration; browser/client storage is outside this repo |
| R14 | Broken object authorization | Records scoped to verified subject; no read/update endpoint | Do not add object read/update using customer_id alone |
| R15 | Request abuse | WAF, method throttling, payload bounds, reserved concurrency | WAF rate limits are approximate; they do not replace service capacity planning |
| R16 | Data loss | DynamoDB PITR and deletion protection | Restore is into another table; application cutover must be tested |
| R17 | Unexpected cost | Separate roots, documented cost drivers and cleanup | No automatic shutdown; protected/non-empty data resources can block destroy |
| R18 | Dependency drift | Pinned Terraform providers; dependency lock | Runtime SDK is AWS-managed; pin packaged dependencies before production |
| R19 | Source/state disclosure | Ignore rules and publication checklist | Review untracked files; .gitignore alone does not remove tracked secrets |
| R20 | Unverified AWS compatibility | CI validate/mock tests and live release gates | This build could not execute provider IPC; complete provider validation before deploy |

No formal compliance certification is claimed. Control intent can support a future assessment, but mapping a label to an AWS setting is not evidence of sustained operating effectiveness.
