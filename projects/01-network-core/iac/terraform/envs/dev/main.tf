locals {
  base_tags = merge(var.tags, {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "Terraform"
  })
}

module "tgw" {
  source = "../../modules/tgw"
  name   = "${var.project}-${var.environment}-tgw"
  asn    = 64512
  tags   = local.base_tags
}

module "vpc_dev" {
  source = "../../modules/vpc"
  name   = "${var.project}-${var.environment}-dev"
  cidr_block = var.cidrs.dev
  create_igw = false
  create_public_rt = false
  subnets = {
    priv_a = { cid = cidrsubnet(var.cidrs.dev, 4, 0), az = var.azs[0], public = false }
    priv_b = { cid = cidrsubnet(var.cidrs.dev, 4, 1), az = var.azs[1], public = false }
  }
  tags = local.base_tags
}

module "vpc_prod" {
  source = "../../modules/vpc"
  name   = "${var.project}-${var.environment}-prod"
  cidr_block = var.cidrs.prod
  create_igw = false
  create_public_rt = false
  subnets = {
    priv_a = { cid = cidrsubnet(var.cidrs.prod, 4, 0), az = var.azs[0], public = false }
    priv_b = { cid = cidrsubnet(var.cidrs.prod, 4, 1), az = var.azs[1], public = false }
  }
  tags = local.base_tags
}

module "vpc_shared" {
  source = "../../modules/vpc"
  name   = "${var.project}-${var.environment}-shared"
  cidr_block = var.cidrs.shared
  create_igw = false
  create_public_rt = false
  subnets = {
    priv_a = { cid = cidrsubnet(var.cidrs.shared, 4, 0), az = var.azs[0], public = false }
    priv_b = { cid = cidrsubnet(var.cidrs.shared, 4, 1), az = var.azs[1], public = false }
  }
  tags = local.base_tags
}

module "vpc_inspect" {
  source = "../../modules/vpc"
  name   = "${var.project}-${var.environment}-inspect"
  cidr_block = var.cidrs.inspect
  create_igw = true
  create_public_rt = true
  subnets = {
    fw_a  = { cid = cidrsubnet(var.cidrs.inspect, 4, 0), az = var.azs[0], public = false }
    fw_b  = { cid = cidrsubnet(var.cidrs.inspect, 4, 1), az = var.azs[1], public = false }
    pub_a = { cid = cidrsubnet(var.cidrs.inspect, 4, 2), az = var.azs[0], public = true }
    pub_b = { cid = cidrsubnet(var.cidrs.inspect, 4, 3), az = var.azs[1], public = true }
  }
  tags = local.base_tags
}

# NAT Gateway for centralized egress
resource "aws_eip" "nat" {
  domain = "vpc"
  tags   = merge(local.base_tags, { Name = "${var.project}-${var.environment}-nat-eip" })
}

resource "aws_nat_gateway" "this" {
  allocation_id = aws_eip.nat.id
  subnet_id     = module.vpc_inspect.subnet_ids["pub_a"]
  tags          = merge(local.base_tags, { Name = "${var.project}-${var.environment}-nat" })
  depends_on    = [module.vpc_inspect]
}

# Private route table in inspection VPC to send egress to NAT
resource "aws_route_table" "inspect_private" {
  vpc_id = module.vpc_inspect.vpc_id
  tags   = merge(local.base_tags, { Name = "${var.project}-${var.environment}-inspect-rt-private" })
}

resource "aws_route" "inspect_private_default" {
  route_table_id         = aws_route_table.inspect_private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.this.id
}

resource "aws_route_table_association" "inspect_fw_a" {
  subnet_id      = module.vpc_inspect.subnet_ids["fw_a"]
  route_table_id = aws_route_table.inspect_private.id
}
resource "aws_route_table_association" "inspect_fw_b" {
  subnet_id      = module.vpc_inspect.subnet_ids["fw_b"]
  route_table_id = aws_route_table.inspect_private.id
}

module "nfw" {
  source = "../../modules/network_firewall"
  name   = "${var.project}-${var.environment}-nfw"
  vpc_id = module.vpc_inspect.vpc_id
  firewall_subnet_ids = [
    module.vpc_inspect.subnet_ids["fw_a"],
    module.vpc_inspect.subnet_ids["fw_b"]
  ]
  log_group_name = "/aws/network-firewall/${var.project}/${var.environment}"
  retention_days = 30
  tags = local.base_tags
}

# Flow logs for each VPC
module "flow_dev" {
  source         = "../../modules/flow_logs"
  name           = "${var.project}-${var.environment}-dev"
  vpc_id         = module.vpc_dev.vpc_id
  log_group_name = "/aws/vpc-flow/${var.project}/${var.environment}/dev"
  retention_days = 30
  tags           = local.base_tags
}

module "flow_prod" {
  source         = "../../modules/flow_logs"
  name           = "${var.project}-${var.environment}-prod"
  vpc_id         = module.vpc_prod.vpc_id
  log_group_name = "/aws/vpc-flow/${var.project}/${var.environment}/prod"
  retention_days = 30
  tags           = local.base_tags
}

module "flow_shared" {
  source         = "../../modules/flow_logs"
  name           = "${var.project}-${var.environment}-shared"
  vpc_id         = module.vpc_shared.vpc_id
  log_group_name = "/aws/vpc-flow/${var.project}/${var.environment}/shared"
  retention_days = 30
  tags           = local.base_tags
}

module "flow_inspect" {
  source         = "../../modules/flow_logs"
  name           = "${var.project}-${var.environment}-inspect"
  vpc_id         = module.vpc_inspect.vpc_id
  log_group_name = "/aws/vpc-flow/${var.project}/${var.environment}/inspect"
  retention_days = 30
  tags           = local.base_tags
}

# TGW attachments
module "att_dev" {
  source = "../../modules/tgw_attachment"
  name   = "${var.project}-${var.environment}-att-dev"
  tgw_id = module.tgw.tgw_id
  vpc_id = module.vpc_dev.vpc_id
  subnet_ids = [
    module.vpc_dev.subnet_ids["priv_a"],
    module.vpc_dev.subnet_ids["priv_b"]
  ]
  associate_rt_id = module.tgw.rt_spokes_id
  propagate_rt_id = module.tgw.rt_hub_id
  tags = local.base_tags
}

module "att_prod" {
  source = "../../modules/tgw_attachment"
  name   = "${var.project}-${var.environment}-att-prod"
  tgw_id = module.tgw.tgw_id
  vpc_id = module.vpc_prod.vpc_id
  subnet_ids = [
    module.vpc_prod.subnet_ids["priv_a"],
    module.vpc_prod.subnet_ids["priv_b"]
  ]
  associate_rt_id = module.tgw.rt_spokes_id
  propagate_rt_id = module.tgw.rt_hub_id
  tags = local.base_tags
}

module "att_shared" {
  source = "../../modules/tgw_attachment"
  name   = "${var.project}-${var.environment}-att-shared"
  tgw_id = module.tgw.tgw_id
  vpc_id = module.vpc_shared.vpc_id
  subnet_ids = [
    module.vpc_shared.subnet_ids["priv_a"],
    module.vpc_shared.subnet_ids["priv_b"]
  ]
  associate_rt_id = module.tgw.rt_spokes_id
  propagate_rt_id = module.tgw.rt_hub_id
  tags = local.base_tags
}

module "att_inspect" {
  source = "../../modules/tgw_attachment"
  name   = "${var.project}-${var.environment}-att-inspect"
  tgw_id = module.tgw.tgw_id
  vpc_id = module.vpc_inspect.vpc_id
  subnet_ids = [
    module.vpc_inspect.subnet_ids["fw_a"],
    module.vpc_inspect.subnet_ids["fw_b"]
  ]
  associate_rt_id = module.tgw.rt_hub_id
  propagate_rt_id = module.tgw.rt_spokes_id
  tags = local.base_tags
}

# TGW routes: spokes default -> inspection
resource "aws_ec2_transit_gateway_route" "spokes_default" {
  destination_cidr_block         = "0.0.0.0/0"
  transit_gateway_attachment_id  = module.att_inspect.attachment_id
  transit_gateway_route_table_id = module.tgw.rt_spokes_id
}

# TGW routes: hub back to spokes
resource "aws_ec2_transit_gateway_route" "hub_to_dev" {
  destination_cidr_block         = var.cidrs.dev
  transit_gateway_attachment_id  = module.att_dev.attachment_id
  transit_gateway_route_table_id = module.tgw.rt_hub_id
}
resource "aws_ec2_transit_gateway_route" "hub_to_prod" {
  destination_cidr_block         = var.cidrs.prod
  transit_gateway_attachment_id  = module.att_prod.attachment_id
  transit_gateway_route_table_id = module.tgw.rt_hub_id
}
resource "aws_ec2_transit_gateway_route" "hub_to_shared" {
  destination_cidr_block         = var.cidrs.shared
  transit_gateway_attachment_id  = module.att_shared.attachment_id
  transit_gateway_route_table_id = module.tgw.rt_hub_id
}

output "tgw_id" { value = module.tgw.tgw_id }
output "inspect_vpc_id" { value = module.vpc_inspect.vpc_id }
output "nfw_arn" { value = module.nfw.firewall_arn }
