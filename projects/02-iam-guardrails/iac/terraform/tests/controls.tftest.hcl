mock_provider "aws" {
  mock_data "aws_caller_identity" {
    defaults = { account_id = "111122223333", arn = "arn:aws:iam::111122223333:root", user_id = "mock" }
  }
  mock_data "aws_partition" {
    defaults = { partition = "aws", dns_suffix = "amazonaws.com" }
  }
}
mock_provider "archive" {}
variables {
  account_id                = "111122223333"
  name                      = "sandbox-test"
  trusted_principal_arns    = ["arn:aws:iam::111122223333:role/Operator"]
  breakglass_principal_arns = ["arn:aws:iam::111122223333:user/Emergency"]
}
run "security_configuration" {
  command = plan
  assert {
    condition     = length(aws_organizations_policy_attachment.guardrail) == 0
    error_message = "Organization mutation must be opt-in."
  }
  assert {
    condition     = aws_iam_role.breakglass.max_session_duration == 3600
    error_message = "Emergency sessions are capped at one hour."
  }
}
run "reject_wrong_account_format" {
  command = plan
  variables { account_id = "invalid" }
  expect_failures = [var.account_id]
}
