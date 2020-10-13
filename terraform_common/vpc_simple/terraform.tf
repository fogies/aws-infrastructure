/*
 * Simple VPC with single Subnet in single Availability Zone.
 * - Includes an Internet Gateway, so instances have Internet access.
 */

/*
 * Explicit configuration of providers.
 */
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.9.0"
    }
  }
}

/*
 * Tags applied within this module.
 */
locals {
  module_tags = {
    terraform = true
  }
}

/*
 * The VPC and the Subnet.
 */
resource "aws_vpc" "vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    var.tags,
    local.module_tags,
    {
    },
  )
}

resource "aws_subnet" "subnet" {
  vpc_id            = aws_vpc.vpc.id
  availability_zone = var.aws_availability_zone
  cidr_block        = cidrsubnet(aws_vpc.vpc.cidr_block, 4, 0)

  map_public_ip_on_launch = var.map_public_ip_on_launch

  tags = merge(
    var.tags,
    local.module_tags,
    {
    },
  )
}

/*
 * An Internet Gateway with a route.
 */
resource "aws_internet_gateway" "gateway" {
  vpc_id = aws_vpc.vpc.id

  tags = merge(
    var.tags,
    local.module_tags,
    {
    },
  )
}

resource "aws_route_table" "route" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gateway.id
  }

  tags = merge(
    var.tags,
    local.module_tags,
    {
    },
  )
}

resource "aws_route_table_association" "route" {
  subnet_id      = aws_subnet.subnet.id
  route_table_id = aws_route_table.route.id
}
