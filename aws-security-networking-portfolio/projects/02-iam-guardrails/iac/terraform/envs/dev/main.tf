locals {
  base_tags = merge(var.tags, {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "Terraform"
  })
}

resource "random_id" "suffix" {
  byte_length = 3
}

# S3 bucket for CloudTrail logs (SSE-S3 for simplicity; KMS is a recommended enhancement)
resource "aws_s3_bucket" "cloudtrail" {
  bucket = "${var.project}-${var.environment}-cloudtrail-${random_id.suffix.hex}"
  tags   = local.base_tags
}

resource "aws_s3_bucket_versioning" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_public_access_block" "cloudtrail" {
  bucket                  = aws_s3_bucket.cloudtrail.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

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
  name               = "${var.project}-${var.environment}-cloudtrail-to-cw"
  assume_role_policy = data.aws_iam_policy_document.trail_assume.json
  tags               = local.base_tags
}

resource "aws_iam_role_policy" "trail_to_cw" {
  name = "${var.project}-${var.environment}-cloudtrail-to-cw"
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
  s3_bucket_name                = aws_s3_bucket.cloudtrail.bucket
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true

  cloud_watch_logs_group_arn = "${aws_cloudwatch_log_group.trail.arn}:*"
  cloud_watch_logs_role_arn  = aws_iam_role.trail_to_cw.arn

  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }

  tags = local.base_tags
}

# SNS for alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.project}-${var.environment}-iam-alerts"
  tags = local.base_tags
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.security_alert_email
}

# Permission boundary: blocks IAM privilege escalation patterns
resource "aws_iam_policy" "permission_boundary" {
  name        = "${var.project}-${var.environment}-perm-boundary"
  description = "Permission boundary limiting IAM escalation and restricting dangerous actions."
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyIAMPrivilegeEscalation"
        Effect = "Deny"
        Action = [
          "iam:CreatePolicy",
          "iam:CreatePolicyVersion",
          "iam:SetDefaultPolicyVersion",
          "iam:AttachUserPolicy",
          "iam:AttachRolePolicy",
          "iam:PutUserPolicy",
          "iam:PutRolePolicy",
          "iam:UpdateAssumeRolePolicy",
          "iam:CreateAccessKey",
          "iam:UpdateAccessKey",
          "iam:DeleteAccessKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyPublicS3PolicyChanges"
        Effect = "Deny"
        Action = [
          "s3:PutBucketPolicy",
          "s3:PutBucketAcl",
          "s3:PutObjectAcl"
        ]
        Resource = "*"
      }
    ]
  })
  tags = local.base_tags
}

# Read-only auditor role
data "aws_iam_policy_document" "auditor_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals { type = "AWS", identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"] }
  }
}
data "aws_caller_identity" "current" {}

resource "aws_iam_role" "auditor" {
  name               = "ReadOnlyAuditorRole"
  assume_role_policy = data.aws_iam_policy_document.auditor_trust.json
  permissions_boundary = aws_iam_policy.permission_boundary.arn
  tags = local.base_tags
}

resource "aws_iam_role_policy_attachment" "auditor_ro" {
  role       = aws_iam_role.auditor.name
  policy_arn  = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# Incident responder role: read GuardDuty/SecurityHub/CloudTrail plus CloudWatch logs access
resource "aws_iam_role" "ir" {
  name               = "IncidentResponderRole"
  assume_role_policy = data.aws_iam_policy_document.auditor_trust.json
  permissions_boundary = aws_iam_policy.permission_boundary.arn
  tags = local.base_tags
}

resource "aws_iam_role_policy" "ir_inline" {
  name = "IncidentResponderInline"
  role = aws_iam_role.ir.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "guardduty:List*",
          "guardduty:Get*",
          "securityhub:Get*",
          "securityhub:Describe*",
          "securityhub:List*",
          "cloudtrail:LookupEvents",
          "logs:FilterLogEvents",
          "logs:GetLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "*"
      }
    ]
  })
}

# Deployer role: sample least-privilege for serverless deploy (limited)
resource "aws_iam_role" "deployer" {
  name               = "DeployerRole"
  assume_role_policy = data.aws_iam_policy_document.auditor_trust.json
  permissions_boundary = aws_iam_policy.permission_boundary.arn
  tags = local.base_tags
}

resource "aws_iam_role_policy" "deployer_inline" {
  name = "DeployerInline"
  role = aws_iam_role.deployer.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:CreateFunction",
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:GetFunction",
          "lambda:ListFunctions",
          "apigateway:GET",
          "apigateway:POST",
          "apigateway:PUT",
          "apigateway:DELETE",
          "iam:PassRole",
          "cloudwatch:PutMetricAlarm",
          "cloudwatch:DescribeAlarms",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Break-glass admin role: MFA required + monitored
data "aws_iam_policy_document" "breakglass_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals { type = "AWS", identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"] }
    condition {
      test     = "Bool"
      variable = "aws:MultiFactorAuthPresent"
      values   = ["true"]
    }
  }
}

resource "aws_iam_role" "breakglass" {
  name               = "BreakGlassAdminRole"
  assume_role_policy = data.aws_iam_policy_document.breakglass_trust.json
  max_session_duration = 3600
  tags = local.base_tags
}

resource "aws_iam_role_policy_attachment" "breakglass_admin" {
  role      = aws_iam_role.breakglass.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# CloudWatch alarms from CloudTrail log group - filter patterns
resource "aws_cloudwatch_log_metric_filter" "risky_iam" {
  name           = "${var.project}-${var.environment}-risky-iam"
  log_group_name = aws_cloudwatch_log_group.trail.name
  pattern        = "{ ($.eventSource = iam.amazonaws.com) && (($.eventName = CreatePolicyVersion) || ($.eventName = AttachUserPolicy) || ($.eventName = AttachRolePolicy) || ($.eventName = PutRolePolicy) || ($.eventName = PutUserPolicy) || ($.eventName = UpdateAssumeRolePolicy)) }"

  metric_transformation {
    name      = "RiskyIAMActions"
    namespace = "Portfolio/IAM"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "risky_iam_alarm" {
  alarm_name          = "${var.project}-${var.environment}-risky-iam-alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.risky_iam.metric_transformation[0].name
  namespace           = aws_cloudwatch_log_metric_filter.risky_iam.metric_transformation[0].namespace
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alerts on risky IAM actions detected via CloudTrail."
  alarm_actions       = [aws_sns_topic.alerts.arn]
  tags                = local.base_tags
}

# Alarm for BreakGlass usage
resource "aws_cloudwatch_log_metric_filter" "breakglass_assume" {
  name           = "${var.project}-${var.environment}-breakglass-assume"
  log_group_name = aws_cloudwatch_log_group.trail.name
  pattern        = "{ ($.eventName = AssumeRole) && ($.requestParameters.roleArn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/BreakGlassAdminRole") }"

  metric_transformation {
    name      = "BreakGlassAssume"
    namespace = "Portfolio/IAM"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "breakglass_alarm" {
  alarm_name          = "${var.project}-${var.environment}-breakglass-alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.breakglass_assume.metric_transformation[0].name
  namespace           = aws_cloudwatch_log_metric_filter.breakglass_assume.metric_transformation[0].namespace
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alerts when BreakGlassAdminRole is assumed."
  alarm_actions       = [aws_sns_topic.alerts.arn]
  tags                = local.base_tags
}

output "permission_boundary_arn" { value = aws_iam_policy.permission_boundary.arn }
output "cloudtrail_bucket" { value = aws_s3_bucket.cloudtrail.bucket }
output "alerts_topic_arn" { value = aws_sns_topic.alerts.arn }
