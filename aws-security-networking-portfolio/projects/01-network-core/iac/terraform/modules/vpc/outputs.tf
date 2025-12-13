output "vpc_id" { value = aws_vpc.this.id }
output "subnet_ids" { value = { for k, s in aws_subnet.subnets : k => s.id } }
output "igw_id" { value = try(aws_internet_gateway.this[0].id, null) }
