variable "name" { type = string }
variable "cidr_block" { type = string }
variable "create_igw" { type = bool  default = false }
variable "create_public_rt" { type = bool default = false }

variable "subnets" {
  description = "Map of subnets: key -> {cid, az, public}"
  type = map(object({
    cid   = string
    az    = string
    public = bool
  }))
}

variable "tags" { type = map(string) default = {} }
