variable "name" { type = string }
variable "vpc_id" { type = string }
variable "log_group_name" { type = string }
variable "retention_days" { type = number default = 30 }
variable "tags" { type = map(string) default = {} }
