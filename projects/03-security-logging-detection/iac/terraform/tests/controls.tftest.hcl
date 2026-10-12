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
    condition     = aws_opensearch_domain.search.cluster_config[0].zone_awareness_enabled
    error_message = "Search must span two AZs."
  }
  assert {
    condition     = aws_opensearch_domain.search.domain_endpoint_options[0].enforce_https
    error_message = "Search requires TLS."
  }
  assert {
    condition     = aws_lambda_function_event_invoke_config.ingest.maximum_retry_attempts == 2
    error_message = "Processing failures must have bounded retries."
  }
}
run "reject_wrong_account_format" {
  command = plan
  variables { account_id = "invalid" }
  expect_failures = [var.account_id]
}
