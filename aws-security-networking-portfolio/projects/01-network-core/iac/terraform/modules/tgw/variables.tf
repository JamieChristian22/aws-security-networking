variable "name" { type = string }
variable "asn" { type = number default = 64512 }
variable "tags" { type = map(string) default = {} }
