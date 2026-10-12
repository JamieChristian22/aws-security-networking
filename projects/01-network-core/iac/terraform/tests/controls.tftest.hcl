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
    condition     = aws_ec2_transit_gateway.core.default_route_table_propagation == "disable"
    error_message = "Implicit route propagation must remain disabled."
  }
  assert {
    condition     = aws_ec2_transit_gateway_vpc_attachment.inspection.appliance_mode_support == "enable"
    error_message = "Stateful inspection requires AZ affinity."
  }
  assert {
    condition     = length(aws_nat_gateway.egress) == 2
    error_message = "Each AZ needs its own egress NAT."
  }
  assert {
    condition     = alltrue([for r in aws_ec2_transit_gateway_route.block_east_west : r.blackhole])
    error_message = "Cross-spoke routes must be blackholes."
  }
}
run "reject_wrong_account_format" {
  command = plan
  variables { account_id = "invalid" }
  expect_failures = [var.account_id]
}
