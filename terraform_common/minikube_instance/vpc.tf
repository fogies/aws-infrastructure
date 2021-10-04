/*
 * Resolve our VPC and Subnet variables, either as created or as provided.
 */
locals {
  resolved_vpc_id = var.create_vpc ? one(module.vpc).vpc_id : var.vpc_id
  resolved_vpc_default_security_group_id = var.create_vpc ? one(module.vpc).default_security_group_id : var.vpc_default_security_group_id
  resolved_subnet_id = var.create_vpc ? one(module.vpc).subnet_id : var.subnet_id
}

/*
 * Simple VPC with single subnet in single availability zone.
 */
module "vpc" {
  count = var.create_vpc ? 1 : 0

  source = "../vpc"

  availability_zone = var.availability_zone

  tags = local.module_tags
}
