output "summary" {
  value = {
    api_url              = "${aws_api_gateway_stage.dev.invoke_url}/hello"
    user_pool_id         = aws_cognito_user_pool.this.id
    user_pool_client_id  = aws_cognito_user_pool_client.this.id
    kms_key_arn          = aws_kms_key.this.arn
    waf_arn              = aws_wafv2_web_acl.this.arn
    alerts_topic         = aws_sns_topic.alerts.arn
  }
}
