/*
 * VPC created for use by Packer.
 */
output "vpc_id" {
  value = module.vpc.vpc_id
}

/*
 * Subnet created for use by Packer.
 */
output "subnet_id" {
  value = module.vpc.subnet_id
}
