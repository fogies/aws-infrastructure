/*
 * Explicit configuration of providers.
 */

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
    local = {
      source = "hashicorp/local"
    }
    tls = {
      source = "hashicorp/tls"
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
  packernetwork_build_id        = random_uuid.packernetwork_build_id.result

  project_tags = {
    terraform = true

    packernetwork                 = true
    packernetwork_build_id        = local.packernetwork_build_id

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
 * VPC and Subnet:
 * - With an Internet Gateway, so instances have Internet access.
 * - Public IP addresses, so instances are visible to the Internet.
 *   - Needed so Packer can SSH to the instance it will create.
 *   - Packer applies a security group to limit access to that instance.
 */

resource "aws_vpc" "vpc" {
  cidr_block         = "10.0.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true

  tags = merge(
    local.project_tags,
    {
    },
  )
}

resource "aws_internet_gateway" "gateway" {
  vpc_id = aws_vpc.vpc.id

  tags = merge(
    local.project_tags,
    {
    },
  )
}

resource "aws_subnet" "subnet" {
  vpc_id            = aws_vpc.vpc.id
  availability_zone = var.aws_availability_zone
  cidr_block        = cidrsubnet(aws_vpc.vpc.cidr_block, 4, 0)

  map_public_ip_on_launch = true

  tags = merge(
    local.project_tags,
    {
    },
  )
}

resource "aws_route_table" "route" {
  vpc_id = aws_vpc.vpc.id

  # Route through Internet Gateway
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gateway.id
  }

  tags = merge(
    local.project_tags,
    {
    },
  )
}

resource "aws_route_table_association" "route" {
  subnet_id      = aws_subnet.subnet.id
  route_table_id = aws_route_table.route.id
}

/*
 * Output the ID of our VPC and Subnet for use by Packer.
 */

resource "local_file" "packer_variables" {
  filename = "packernetwork.pkrvars.hcl"
  content  = <<-EOT
    packernetwork_vpc_id = "${aws_vpc.vpc.id}"
    packernetwork_subnet_id = "${aws_subnet.subnet.id}"
  EOT
}
