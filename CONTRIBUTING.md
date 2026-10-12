# Contributing

Create a branch, explain the control or failure scenario, and update implementation, tests and docs together. Run `make validate` and `make terraform-check`. Do not add a PASS row for an unexecuted check. Provider changes require lockfile review; deployment changes require a real plan in the target sandbox. Do not commit state, tokens, customer data or unredacted runtime evidence. Keep one canonical Terraform root per project.
