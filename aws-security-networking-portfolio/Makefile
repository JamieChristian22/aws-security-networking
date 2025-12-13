SHELL := /bin/bash

help:
	@echo "Targets:"
	@echo "  tree      - print repo tree (depth 4)"
	@echo "  fmt       - terraform fmt (all projects)"
	@echo "  validate  - terraform validate for each env/dev"

tree:
	@find . -maxdepth 4 -type f | sed 's|^\./||' | sort

fmt:
	@find projects -type f -name '*.tf' -print0 | xargs -0 terraform fmt

validate:
	@for d in $$(find projects -type d -path '*/iac/terraform/envs/*' -maxdepth 6); do \
		echo "==> $$d"; \
		(cd $$d && terraform init -backend=false -upgrade >/dev/null && terraform validate); \
	done
