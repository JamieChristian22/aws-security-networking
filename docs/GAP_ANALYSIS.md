# Source review and gap closure

Baseline: upstream commit `6bac950d66ca1411bd664aa0ed891835d0468109`.

| Original gap | Change in this package | Verification / remaining gate |
|---|---|---|
| Root snippets and envs/dev stacks diverged | One canonical Terraform root per project; obsolete implementations removed | Repository structure regression |
| OpenSearch allowed all principals and source IPs | Private VPC domain, TLS, security-group restriction and writer-role document scope | Static assertions; live unauthorized access test pending |
| IAM boundary contained only denies | Explicit read/deployment allow envelope plus escalation/security-service denies | Static assertions; IAM simulation and real role tests pending |
| Malformed Terraform policy strings and inconsistent subnet field names | Replaced with consistently structured Terraform JSON | JSON/config loading checked; provider validation pending due IPC restriction |
| Firewall existed without a complete inspected route | Dedicated TGW/firewall/NAT subnets, AZ-indexed endpoints and return routes | Structural assertions; flow-log and packet tests pending |
| Cross-spoke isolation relied on incomplete routes | Explicit TGW blackholes for all spoke prefixes | Static assertion; dev-to-prod negative test pending |
| Single NAT behind two firewall AZs | One NAT and one firewall endpoint per AZ | Count/path regression; outage drill pending |
| CloudTrail destination authorization incomplete | Bucket policy with service principal, source ARN and delivery prefix; dependency ordering | Static policy checks; delivery verification pending |
| API deployed a different handler than the validator checked | One handler, packaged by Terraform, connected to a real table and endpoint | Static wiring and behavior tests |
| Handler failed on wrong JSON types | Strict object/type/length/action validation and bounded bodies | Executed offline negative cases |
| Duplicate writes not handled | Conditional write, subject-scoped idempotency and conflict response | Executed offline create/replay/conflict tests |
| Detection ingestion swallowed errors | Failures raise; bounded Lambda retries, failure destination and EventBridge DLQ | Executed offline propagation tests; live DLQ exercise pending |
| Finding IDs unsafe as URL path segments | SHA-256 document IDs include finding version | Executed deterministic/versioned ID tests |
| Simulated pass rows resembled execution evidence | NOT_RUN live-test ledger; separate executed local report | Repository content validation |
| CI described but absent | Credential-free Python and Terraform workflow | Workflow provided; no remote run claimed |
| Brief operations outlines | Packet walkthroughs, command-based triage, recovery criteria and release gates | Editorial review; live tabletop still required |

## Deliberate boundaries

This upgrade prioritizes one coherent implementation for each project over retaining every unconnected snippet. Original screenshots are preserved as historical learning material. They do not verify this release. The baseline Git commit identifies all original files if comparison or recovery is needed.

Closing a design gap is distinct from proving a control in AWS. Provider validation, real plans and live acceptance remain explicit release gates. No numerical portfolio score substitutes for those gates.
