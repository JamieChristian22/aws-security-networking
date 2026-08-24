provider "aws" { region = "us-east-1" }

resource "aws_kms_key" "logs" {
  description         = "Security logging encryption key"
  enable_key_rotation = true
}

resource "aws_s3_bucket" "trail" {
  bucket_prefix = "central-security-trail-"
}

resource "aws_s3_bucket_versioning" "trail" {
  bucket = aws_s3_bucket.trail.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_public_access_block" "trail" {
  bucket                  = aws_s3_bucket.trail.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_guardduty_detector" "this" { enable = true }

resource "aws_securityhub_account" "this" {}

resource "aws_sns_topic" "high_findings" {
  name              = "security-high-findings"
  kms_master_key_id = aws_kms_key.logs.id
}
