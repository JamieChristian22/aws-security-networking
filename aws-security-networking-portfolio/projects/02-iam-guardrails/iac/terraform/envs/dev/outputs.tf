output "summary" {
  value = {
    trail_bucket = aws_s3_bucket.cloudtrail.bucket
    trail_log_group = aws_cloudwatch_log_group.trail.name
    perm_boundary = aws_iam_policy.permission_boundary.arn
    break_glass_role = aws_iam_role.breakglass.arn
    alerts_topic = aws_sns_topic.alerts.arn
  }
}
