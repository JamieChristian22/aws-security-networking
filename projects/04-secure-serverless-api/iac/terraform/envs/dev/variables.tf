variable "aws_region" { type = string }
variable "project" { type = string }
variable "environment" { type = string }
variable "security_alert_email" { type = string }
variable "tags" { type = map(string) default = {} }

variable "vpc_cidr" { type = string }
variable "azs" { type = list(string) }
