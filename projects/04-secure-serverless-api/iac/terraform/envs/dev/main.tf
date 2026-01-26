locals {
  base_tags = merge(var.tags, {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "Terraform"
  })
}

resource "random_id" "suffix" { byte_length = 3 }

# VPC + private subnets
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = merge(local.base_tags, { Name = "${var.project}-${var.environment}-vpc" })
}

resource "aws_subnet" "priv_a" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 4, 0)
  availability_zone = var.azs[0]
  tags              = merge(local.base_tags, { Name = "${var.project}-${var.environment}-priv-a" })
}

resource "aws_subnet" "priv_b" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 4, 1)
  availability_zone = var.azs[1]
  tags              = merge(local.base_tags, { Name = "${var.project}-${var.environment}-priv-b" })
}

resource "aws_security_group" "lambda" {
  name        = "${var.project}-${var.environment}-lambda-sg"
  description = "Lambda to VPC endpoints"
  vpc_id      = aws_vpc.this.id

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.base_tags
}

resource "aws_security_group" "vpce" {
  name        = "${var.project}-${var.environment}-vpce-sg"
  description = "VPC endpoint SG"
  vpc_id      = aws_vpc.this.id

  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.base_tags
}

resource "aws_vpc_endpoint" "logs" {
  vpc_id              = aws_vpc.this.id
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.priv_a.id, aws_subnet.priv_b.id]
  security_group_ids  = [aws_security_group.vpce.id]
  private_dns_enabled = true
  tags                = merge(local.base_tags, { Name = "${var.project}-${var.environment}-vpce-logs" })
}

resource "aws_vpc_endpoint" "sts" {
  vpc_id              = aws_vpc.this.id
  service_name        = "com.amazonaws.${var.aws_region}.sts"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.priv_a.id, aws_subnet.priv_b.id]
  security_group_ids  = [aws_security_group.vpce.id]
  private_dns_enabled = true
  tags                = merge(local.base_tags, { Name = "${var.project}-${var.environment}-vpce-sts" })
}

resource "aws_vpc_endpoint" "kms" {
  vpc_id              = aws_vpc.this.id
  service_name        = "com.amazonaws.${var.aws_region}.kms"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.priv_a.id, aws_subnet.priv_b.id]
  security_group_ids  = [aws_security_group.vpce.id]
  private_dns_enabled = true
  tags                = merge(local.base_tags, { Name = "${var.project}-${var.environment}-vpce-kms" })
}

# KMS key
resource "aws_kms_key" "this" {
  description             = "KMS key for portfolio secure serverless API"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  tags                    = local.base_tags
}

resource "aws_kms_alias" "this" {
  name          = "alias/${var.project}-${var.environment}-api"
  target_key_id = aws_kms_key.this.key_id
}

# Cognito User Pool
resource "aws_cognito_user_pool" "this" {
  name = "${var.project}-${var.environment}-users"

  password_policy {
    minimum_length    = 12
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = true
  }

  tags = local.base_tags
}

resource "aws_cognito_user_pool_client" "this" {
  name         = "${var.project}-${var.environment}-app"
  user_pool_id = aws_cognito_user_pool.this.id
  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_ADMIN_USER_PASSWORD_AUTH"
  ]
}

# Lambda
data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals { type = "Service", identifiers = ["lambda.amazonaws.com"] }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.project}-${var.environment}-api-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
  tags               = local.base_tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role      = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_kms" {
  name = "LambdaKMS"
  role = aws_iam_role.lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey"]
      Resource = aws_kms_key.this.arn
    }]
  })
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../../../lambda/app.py"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "this" {
  function_name = "${var.project}-${var.environment}-api"
  role          = aws_iam_role.lambda.arn
  handler       = "app.handler"
  runtime       = "python3.12"

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  vpc_config {
    security_group_ids = [aws_security_group.lambda.id]
    subnet_ids         = [aws_subnet.priv_a.id, aws_subnet.priv_b.id]
  }

  environment {
    variables = {
      KMS_KEY_ARN = aws_kms_key.this.arn
    }
  }

  tags = local.base_tags
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "this" {
  name = "${var.project}-${var.environment}-api"
  endpoint_configuration { types = ["REGIONAL"] }
  tags = local.base_tags
}

resource "aws_api_gateway_resource" "root" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "hello"
}

resource "aws_api_gateway_authorizer" "cognito" {
  name          = "${var.project}-${var.environment}-cognito"
  rest_api_id   = aws_api_gateway_rest_api.this.id
  type          = "COGNITO_USER_POOLS"
  provider_arns = [aws_cognito_user_pool.this.arn]
  identity_source = "method.request.header.Authorization"
}

resource "aws_api_gateway_method" "get" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.root.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "get" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  resource_id = aws_api_gateway_resource.root.id
  http_method = aws_api_gateway_method.get.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri  = aws_lambda_function.this.invoke_arn
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.this.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  triggers = {
    redeploy = sha1(jsonencode([
      aws_api_gateway_integration.get.id,
      aws_api_gateway_method.get.id,
      aws_api_gateway_authorizer.cognito.id
    ]))
  }
  lifecycle { create_before_destroy = true }
}

resource "aws_api_gateway_stage" "dev" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  deployment_id = aws_api_gateway_deployment.this.id
  stage_name    = var.environment
  tags          = local.base_tags
}

# WAFv2
resource "aws_wafv2_web_acl" "this" {
  name  = "${var.project}-${var.environment}-waf"
  scope = "REGIONAL"

  default_action { allow {} }

  rule {
    name     = "RateLimit"
    priority = 1
    action { block {} }
    statement {
      rate_based_statement {
        limit              = 1000
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimit"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedCommonRules"
    priority = 2
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "CommonRules"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "WebACL"
    sampled_requests_enabled   = true
  }

  tags = local.base_tags
}

resource "aws_wafv2_web_acl_association" "api" {
  resource_arn = aws_api_gateway_stage.dev.arn
  web_acl_arn  = aws_wafv2_web_acl.this.arn
}

# Alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.project}-${var.environment}-alerts"
  tags = local.base_tags
}
resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.security_alert_email
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.project}-${var.environment}-lambda-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  dimensions = {
    FunctionName = aws_lambda_function.this.function_name
  }
  alarm_actions = [aws_sns_topic.alerts.arn]
  tags = local.base_tags
}

resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "${var.project}-${var.environment}-lambda-throttles"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  dimensions = {
    FunctionName = aws_lambda_function.this.function_name
  }
  alarm_actions = [aws_sns_topic.alerts.arn]
  tags = local.base_tags
}

output "api_invoke_url" {
  value = "${aws_api_gateway_stage.dev.invoke_url}/hello"
}
output "user_pool_id" { value = aws_cognito_user_pool.this.id }
output "user_pool_client_id" { value = aws_cognito_user_pool_client.this.id }
output "waf_arn" { value = aws_wafv2_web_acl.this.arn }
