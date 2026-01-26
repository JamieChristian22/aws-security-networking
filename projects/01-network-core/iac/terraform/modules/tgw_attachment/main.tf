resource "aws_ec2_transit_gateway_vpc_attachment" "this" {
  subnet_ids         = var.subnet_ids
  transit_gateway_id = var.tgw_id
  vpc_id             = var.vpc_id

  dns_support  = "enable"
  ipv6_support = "disable"

  tags = merge(var.tags, { Name = var.name })
}

resource "aws_ec2_transit_gateway_route_table_association" "assoc" {
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.this.id
  transit_gateway_route_table_id = var.associate_rt_id
}

resource "aws_ec2_transit_gateway_route_table_propagation" "prop" {
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.this.id
  transit_gateway_route_table_id = var.propagate_rt_id
}
