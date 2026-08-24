variable "region" { default = "us-east-1" }

provider "aws" { region = var.region }

resource "aws_ec2_transit_gateway" "core" {
  description                     = "Central security transit gateway"
  default_route_table_association = "disable"
  default_route_table_propagation = "disable"
  tags = { Name = "security-core-tgw" }
}

resource "aws_vpc" "inspection" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "inspection-vpc" }
}

resource "aws_vpc" "dev" {
  cidr_block = "10.10.0.0/16"
  tags = { Name = "dev-spoke" }
}

resource "aws_vpc" "prod" {
  cidr_block = "10.20.0.0/16"
  tags = { Name = "prod-spoke" }
}

resource "aws_vpc" "shared" {
  cidr_block = "10.30.0.0/16"
  tags = { Name = "shared-spoke" }
}

resource "aws_cloudwatch_log_group" "firewall" {
  name              = "/aws/network-firewall/security-core"
  retention_in_days = 30
}
