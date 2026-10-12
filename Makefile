.PHONY: test validate terraform-check

test:
	python -m pytest -q

validate: test
	python validation/validate_portfolio.py

terraform-check:
	@set -eu; for d in projects/*/iac/terraform; do \
	 terraform -chdir="$$d" init -backend=false -input=false -lockfile=readonly; \
	 terraform -chdir="$$d" validate -no-color; \
	 terraform -chdir="$$d" test -no-color; \
	done

.PHONY: evidence
evidence:
	python validation/run_evidence.py
