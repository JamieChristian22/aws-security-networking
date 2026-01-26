variable "name" { type = string }
variable "tgw_id" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }

variable "associate_rt_id" { type = string }
variable "propagate_rt_id" { type = string }
variable "tags" { type = map(string) default = {} }
