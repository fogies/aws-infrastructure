/*
 * Resolve our VPC and Subnet IDs, either as provided or created.
 */
locals {
  resolved_vpc_id = var.create_vpc ? one(module.vpc).vpc_id : var.vpc_id
  resolved_subnet_id = var.create_vpc ? one(module.vpc).subnet_id : var.subnet_id
}

/*
 * Simple VPC with single subnet in single availability zone.
 */
module "vpc" {
  count = var.create_vpc ? 1 : 0

  source = "../vpc_simple"

  availability_zone = var.availability_zone

  tags = local.module_tags
}
