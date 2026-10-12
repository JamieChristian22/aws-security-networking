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
  account_id = "111122223333"
  name       = "sandbox-test"
}
run "security_configuration" {
  command = plan
  assert {
    condition     = aws_api_gateway_method.post.authorization == "COGNITO_USER_POOLS"
    error_message = "API writes must require Cognito."
  }
  assert {
    condition     = aws_dynamodb_table.requests.point_in_time_recovery[0].enabled
    error_message = "Recovery must be enabled."
  }
  assert {
    condition     = aws_cognito_user_pool.users.mfa_configuration == "ON"
    error_message = "MFA must be required."
  }
  assert {
    condition     = aws_api_gateway_method_settings.all.settings[0].data_trace_enabled == false
    error_message = "Payloads must not enter execution logs."
  }
}
run "reject_wrong_account_format" {
  command = plan
  variables { account_id = "invalid" }
  expect_failures = [var.account_id]
}
