provider "aws" { region = "us-east-1" }

resource "aws_iam_policy" "developer_boundary" {
  name = "DeveloperPermissionBoundary"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:Describe*","s3:Get*","s3:List*",
          "lambda:Get*","lambda:List*","logs:Get*","logs:Describe*"
        ]
        Resource = "*"
      },
      {
        Effect = "Deny"
        Action = [
          "iam:CreatePolicyVersion","iam:SetDefaultPolicyVersion",
          "cloudtrail:StopLogging","guardduty:DeleteDetector"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "readonly_auditor" {
  name = "ReadOnlyAuditorRole"
  assume_role_policy = jsonencode({
    Version="2012-10-17",
    Statement=[{Effect="Allow",Principal={AWS="arn:aws:iam::111122223333:root"},Action="sts:AssumeRole"}]
  })
}

resource "aws_iam_role_policy_attachment" "readonly" {
  role       = aws_iam_role.readonly_auditor.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}
