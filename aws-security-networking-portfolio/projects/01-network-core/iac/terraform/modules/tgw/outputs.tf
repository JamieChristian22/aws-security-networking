output "tgw_id" { value = aws_ec2_transit_gateway.this.id }
output "rt_spokes_id" { value = aws_ec2_transit_gateway_route_table.spokes.id }
output "rt_hub_id" { value = aws_ec2_transit_gateway_route_table.hub.id }
