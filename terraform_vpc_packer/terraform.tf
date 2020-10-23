/*
 * Explicit configuration of providers.
 */
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.9.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 1.4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 2.3.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 2.2.0"
    }
  }
}

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
 * AWS Configuration.
 */
provider "aws" {
  profile = var.aws_profile
  region  = var.aws_region
}

/*
 * Simple VPC with single Subnet in single Availability Zone.
 */
module "vpc" {
  source = "../terraform_common/vpc_simple"

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
