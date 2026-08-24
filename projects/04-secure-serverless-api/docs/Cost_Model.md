# Cost Model

Cost drivers are API Gateway requests/data transfer, Lambda invocation/duration, DynamoDB requests/storage/PITR, Cognito MAU, WAF requests/rules, CloudWatch logging, and KMS requests. PAY_PER_REQUEST/on-demand services are appropriate for variable portfolio traffic; steady production traffic should be reviewed for cheaper capacity models.
