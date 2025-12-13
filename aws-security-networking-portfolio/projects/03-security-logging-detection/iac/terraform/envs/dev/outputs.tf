output "summary" {
  value = {
    trail_bucket        = aws_s3_bucket.log_archive.bucket
    trail_log_group     = aws_cloudwatch_log_group.trail.name
    opensearch_endpoint = aws_opensearch_domain.this.endpoint
    alerts_topic        = aws_sns_topic.alerts.arn
  }
}
