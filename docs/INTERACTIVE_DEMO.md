# AWS Security Architecture & Control Explorer

This is an **offline, interactive evidence-navigation demo**, not a scanner, simulator of network packets, or proof of deployed AWS controls.

## Open it

Download and open [demo/security-controls.html](../demo/security-controls.html) with a browser. For the architecture drawings to load, preserve the sibling `diagrams/` directory; alternatively serve the repository through a local static file server.

You can select one of four AWS projects, filter the 28 tracked control scenarios by status, and search for technologies such as MFA, firewall, WAF and recovery. Each scenario links to its implementation directory and the corresponding live acceptance ledger.

## Data provenance

Controls are embedded verbatim from [docs/CONTROL_REGISTER.csv](CONTROL_REGISTER.csv). The source document reports 28 live acceptance scenarios with status `NOT_RUN`; all 28 remain `NOT_RUN` in this UI. Never promote an offline test to `PASS_LIVE` automatically.

`tests/test_architecture_explorer.py` checks byte-for-field parity for all control rows against the source CSV, verifies each path and acceptance ledger, asserts consistent statuses, and tests essential accessibility/offline rendering behaviors. Whenever the register changes, regenerate the snapshot rather than editing UI statuses independently.

## Security and limitations

- No AWS credentials, external JS libraries or external network calls.
- User input is rendered with DOM `textContent`, not HTML markup.
- The project diagrams express intended architecture, not observed packet paths or cloud service telemetry.
- Provider-backed Terraform mock tests are separate from live AWS account acceptance. CI may validate Terraform without applying anything.
- The present `reports/RELEASE.json` and validation report are historical snapshots and do not describe current GitHub Actions status unless explicitly updated with verified run IDs.
