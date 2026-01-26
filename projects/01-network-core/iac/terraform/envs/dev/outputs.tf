output "summary" {
  value = {
    tgw_id        = module.tgw.tgw_id
    dev_vpc       = module.vpc_dev.vpc_id
    prod_vpc      = module.vpc_prod.vpc_id
    shared_vpc    = module.vpc_shared.vpc_id
    inspect_vpc   = module.vpc_inspect.vpc_id
    nfw_arn       = module.nfw.firewall_arn
  }
}
