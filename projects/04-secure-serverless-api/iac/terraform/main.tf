provider "aws" { region = "us-east-1" }

resource "aws_kms_key" "app" {
  description         = "Serverless API data key"
  enable_key_rotation = true
}

resource "aws_dynamodb_table" "requests" {
  name         = "secure-api-requests"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "request_id"

  attribute {
    name = "request_id"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.app.arn
  }

  point_in_time_recovery { enabled = true }
}

resource "aws_cognito_user_pool" "users" {
  name = "secure-api-users"
  mfa_configuration = "OPTIONAL"
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/secure-api"
  retention_in_days = 30
}
