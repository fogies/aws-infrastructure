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
 * - Generate a random packernetwork_build_id to include in tags.
 */

resource "random_uuid" "packernetwork_build_id" {
}

locals {
  packernetwork_build_id = random_uuid.packernetwork_build_id.result

  project_tags = {
    terraform = true

    packernetwork          = true
    packernetwork_build_id = local.packernetwork_build_id

    packernetwork_project = var.packernetwork_project
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
    local.project_tags,
    {
    },
  )
}

/*
 * Output the ID of VPC and Subnet for use by Packer.
 */
resource "local_file" "packer_variables" {
  filename = "packernetwork.pkrvars.hcl"
  content  = <<-EOT
    packernetwork_vpc_id = "${module.vpc.vpc_id}"
    packernetwork_subnet_id = "${module.vpc.subnet_id}"
  EOT
}
