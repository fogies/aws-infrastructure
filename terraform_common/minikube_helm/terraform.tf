/*
 * Tags to apply to created resources.
 */
locals {
  module_tags = {
  }
}

/*
 * Simple VPC with single Subnet in single Availability Zone.
 */
module "vpc" {
  source = "../vpc_simple"

  availability_zones = [var.aws_availability_zone]

  tags = merge(
    var.tags,
    local.module_tags,
    {
    },
  )
}

/*
 * Security groups for our instance.
 */
module "instance_security_groups" {
  source = "../security_groups"

  vpc_id = module.vpc.vpc_id

  allow_egress_to_anywhere = true
  allow_http_from_anywhere = true
  allow_ssh_from_anywhere  = true

  tags = merge(
    var.tags,
    local.module_tags,
    {
    },
  )
}

/*
 * ID of the AMI we want.
 */
module "ami_minikube" {
  source = "../ami_minikube"

  configuration = var.ami_configuration
}

/*
 * Key pair to support SSH access.
 */
resource "tls_private_key" "instance_key_pair" {
  algorithm = "RSA"
}

resource "aws_key_pair" "instance_key_pair" {
  key_name_prefix = "minikube-"
  public_key      = tls_private_key.instance_key_pair.public_key_openssh

  tags = merge(
    var.tags,
    local.module_tags,
    {
    },
  )
}

/*
 * The actual instance.
 */
resource "aws_instance" "minikube" {
  ami = module.ami_minikube.id

  instance_type = var.aws_instance_type

  subnet_id         = module.vpc.subnet_id

  vpc_security_group_ids = module.instance_security_groups.security_group_ids

  key_name = aws_key_pair.instance_key_pair.id

  tags = merge(
    var.tags,
    local.module_tags,
    {
    },
  )
}
