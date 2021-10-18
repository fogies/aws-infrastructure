/*
 * Tags to apply to resources:
 * - Generate a random vpc_packer_id to include in tags.
 */
resource "random_uuid" "vpc_packer_id" {
}

locals {
  vpc_packer_id = format("vpc-packer-%s", random_uuid.vpc_packer_id.result)

  module_tags = {
    terraform     = true
    vpc_packer_id = local.vpc_packer_id
  }
}

/*
 * Simple VPC with single Subnet in single Availability Zone.
 */
module "vpc" {
  source = "../terraform_common/vpc"

  aws_availability_zone = var.aws_availability_zone

  # Public IP required for Packer to SSH to created instance.
  # Packer applies a security group to limit access to that instance.
  map_public_ip_on_launch = true

  tags = merge(
    var.tags,
    local.module_tags,
    {
    },
  )
}
