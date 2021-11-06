/*
 * Simple VPC used by Packer to create instance.
 */
module "vpc" {
  source = "../terraform_common/vpc"

  availability_zone = "us-east-1a"

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
