variable "aws_region" { type = string }
variable "project" { type = string }
variable "environment" { type = string }

variable "tags" { type = map(string) default = {} }

variable "cidrs" {
  type = object({
    dev     = string
    prod    = string
    shared  = string
    inspect = string
  })
}

variable "azs" {
  description = "Exactly 2 AZs for a minimal, HA-aware footprint."
  type        = list(string)
}

