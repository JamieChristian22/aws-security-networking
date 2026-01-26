locals {
  base_tags = merge(var.tags, {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "Terraform"
  })
}

resource "random_id" "suffix" { byte_length = 3 }

# Log archive bucket
resource "aws_s3_bucket" "log_archive" {
  bucket = "${var.project}-${var.environment}-logs-${random_id.suffix.hex}"
  tags   = local.base_tags
}
resource "aws_s3_bucket_versioning" "log_archive" {
  bucket = aws_s3_bucket.log_archive.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_public_access_block" "log_archive" {
  bucket                  = aws_s3_bucket.log_archive.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudTrail -> S3 + CloudWatch Logs
resource "aws_cloudwatch_log_group" "trail" {
  name              = "/aws/cloudtrail/${var.project}/${var.environment}"
  retention_in_days = 30
  tags              = local.base_tags
}

data "aws_iam_policy_document" "trail_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals { type = "Service", identifiers = ["cloudtrail.amazonaws.com"] }
  }
}
resource "aws_iam_role" "trail_to_cw" {
  name               = "${var.project}-${var.environment}-trail-to-cw"
  assume_role_policy = data.aws_iam_policy_document.trail_assume.json
  tags               = local.base_tags
}
resource "aws_iam_role_policy" "trail_to_cw" {
  name = "${var.project}-${var.environment}-trail-to-cw"
  role = aws_iam_role.trail_to_cw.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["logs:CreateLogStream", "logs:PutLogEvents"]
      Resource = "${aws_cloudwatch_log_group.trail.arn}:*"
    }]
  })
}

resource "aws_cloudtrail" "this" {
  name                          = "${var.project}-${var.environment}-trail"
  s3_bucket_name                = aws_s3_bucket.log_archive.bucket
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  cloud_watch_logs_group_arn    = "${aws_cloudwatch_log_group.trail.arn}:*"
  cloud_watch_logs_role_arn     = aws_iam_role.trail_to_cw.arn

  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }

  tags = local.base_tags
}

# GuardDuty
resource "aws_guardduty_detector" "this" {
  enable = true
  tags   = local.base_tags
}

# Security Hub
resource "aws_securityhub_account" "this" {}

resource "aws_securityhub_standards_subscription" "fsbp" {
  standards_arn = "arn:aws:securityhub:${var.aws_region}::standards/aws-foundational-security-best-practices/v/1.0.0"
  depends_on    = [aws_securityhub_account.this]
}

# OpenSearch domain (smallest reasonable for portfolio)
resource "aws_opensearch_domain" "this" {
  domain_name    = "${var.project}-${var.environment}-sec"
  engine_version = "OpenSearch_2.11"

  cluster_config {
    instance_type  = "t3.small.search"
    instance_count = 1
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 20
  }

  encrypt_at_rest { enabled = true }
  node_to_node_encryption { enabled = true }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { AWS = "*" }
      Action = "es:*"
      Resource = "arn:aws:es:${var.aws_region}:${data.aws_caller_identity.current.account_id}:domain/${var.project}-${var.environment}-sec/*"
      Condition = {
        IpAddress = { "aws:SourceIp": ["0.0.0.0/0"] }
      }
    }]
  })

  tags = local.base_tags
}

# NOTE: The access policy above is intentionally open to ease portfolio testing.
# In a real environment, restrict by IAM principals and SourceIp to your office/VPN, or put the domain in a VPC.

data "aws_caller_identity" "current" {}

# Lambda role to write to OpenSearch
data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals { type = "Service", identifiers = ["lambda.amazonaws.com"] }
  }
}

resource "aws_iam_role" "ingest" {
  name               = "${var.project}-${var.environment}-sh-ingest"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
  tags               = local.base_tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.ingest.name
  policy_arn  = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Allow Lambda to access OpenSearch HTTP endpoint
resource "aws_iam_role_policy" "ingest_es" {
  name = "IngestToOpenSearch"
  role = aws_iam_role.ingest.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "es:ESHttpGet",
        "es:ESHttpPut",
        "es:ESHttpPost"
      ]
      Resource = "${aws_opensearch_domain.this.arn}/*"
    }]
  })
}

# Package lambda
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../../../lambda/ingest_securityhub.py"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "ingest" {
  function_name = "${var.project}-${var.environment}-sh-ingest"
  role          = aws_iam_role.ingest.arn
  handler       = "ingest_securityhub.handler"
  runtime       = "python3.12"

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      OPENSEARCH_ENDPOINT = aws_opensearch_domain.this.endpoint
      INDEX_PREFIX        = "securityhub-findings"
      TIME_FIELD          = "CreatedAt"
    }
  }

  tags = local.base_tags
}

# EventBridge rule: all Security Hub findings -> Lambda
resource "aws_cloudwatch_event_rule" "sh_findings_all" {
  name        = "${var.project}-${var.environment}-sh-findings-all"
  description = "Send all Security Hub findings to ingestion Lambda"
  event_pattern = jsonencode({
    "source": ["aws.securityhub"],
    "detail-type": ["Security Hub Findings - Imported"]
  })
  tags = local.base_tags
}

resource "aws_cloudwatch_event_target" "to_lambda" {
  rule      = aws_cloudwatch_event_rule.sh_findings_all.name
  target_id = "IngestLambda"
  arn       = aws_lambda_function.ingest.arn
}

resource "aws_lambda_permission" "allow_events" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.sh_findings_all.arn
}

# Alerts: HIGH/CRITICAL findings -> SNS email
resource "aws_sns_topic" "alerts" {
  name = "${var.project}-${var.environment}-alerts"
  tags = local.base_tags
}
resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.security_alert_email
}

resource "aws_cloudwatch_event_rule" "sh_high" {
  name = "${var.project}-${var.environment}-sh-high"
  event_pattern = jsonencode({
    "source": ["aws.securityhub"],
    "detail-type": ["Security Hub Findings - Imported"],
    "detail": {
      "findings": {
        "Severity": { "Label": ["HIGH", "CRITICAL"] }
      }
    }
  })
  tags = local.base_tags
}

resource "aws_cloudwatch_event_target" "to_sns" {
  rule      = aws_cloudwatch_event_rule.sh_high.name
  target_id = "SNSTopic"
  arn       = aws_sns_topic.alerts.arn
}

output "opensearch_endpoint" { value = aws_opensearch_domain.this.endpoint }
output "trail_bucket" { value = aws_s3_bucket.log_archive.bucket }
output "alerts_topic" { value = aws_sns_topic.alerts.arn }
