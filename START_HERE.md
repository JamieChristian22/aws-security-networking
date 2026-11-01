# Start Here — AWS Security & Networking Portfolio

This is an educational AWS security engineering repository. The four AWS projects include implemented Terraform definitions, Python handlers and offline tests, but **live AWS deployment and live-security acceptance are not yet verified**.

## Two-minute review

1. Read the [portfolio overview](README.md) and examine the [architecture diagram](diagrams/portfolio.svg).
2. Open the [interactive control explorer](demo/security-controls.html) locally to filter all 28 planned live acceptance scenarios. Their recorded status is `NOT_RUN`, not PASS.
3. Review [test coverage and limits](docs/TEST_STRATEGY.md), [control traceability](docs/CONTROL_TEST_TRACEABILITY.csv) and [evidence standard](docs/EVIDENCE.md).
4. Review the [CI workflow](.github/workflows/aws-security-ci.yml) and the actual branch run to distinguish successful offline tests from Terraform mock tests and live acceptance.

## Offline reproduction

Use Python 3.12 and a clean virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python validation/validate_portfolio.py
python -m pytest -q
python validation/run_evidence.py
```

No AWS account is necessary for those offline checks. `run_evidence.py` records exit codes and run artifacts under `reports/`.

## Terraform validation (no deployment)

Install Terraform 1.9.8 and run `make terraform-check`. The four independent Terraform roots initialize pinned provider versions, validate their configurations and run mock-provider assertions. Provider binaries require initial internet access. The command does not call `terraform apply` and does not establish live AWS safety. Provider lockfiles, which are currently absent from the published GitHub baseline, should be reviewed and version-controlled before production-oriented promotion.

## Release verification

`python scripts/verify_release.py` intentionally reports a failure when `MANIFEST.sha256` is absent. Generate and review a release manifest during packaging before claiming checksum verification. Existing `reports/RELEASE.json` is an older evidence snapshot.

## AWS deployment and costs

Deploy only to an explicitly authorized disposable sandbox after reviewing [deployment requirements](docs/DEPLOYMENT.md), [costs and cleanup](docs/COSTS_AND_CLEANUP.md), and [release readiness](docs/RELEASE_READINESS.md). This repository does not deploy by itself.
