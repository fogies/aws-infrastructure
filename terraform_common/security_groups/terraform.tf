/*
 * Commonly-used network security groups.
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
 * Allow egress to anywhere.
 */
resource "aws_security_group" "allow_egress_to_anywhere" {
  /*
   * Only created if var.allow_egress_to_anywhere is true.
   */
  count = var.allow_egress_to_anywhere ? 1 : 0

  name_prefix = "allow_egress_to_anywhere-"

  vpc_id = var.vpc_id

  egress {
    description = "Allow Egress to Anywhere"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    var.tags,
    local.module_tags,
    {
      Name = "Allow Egress to Anywhere"
    },
  )
}

/*
 * Allow HTTP and HTTPS from anywhere.
 */
resource "aws_security_group" "allow_http_from_anywhere" {
  /*
   * Only created if var.allow_http_from_anywhere is true.
   */
  count = var.allow_http_from_anywhere ? 1 : 0

  name_prefix = "allow_http_from_anywhere-"

  vpc_id = var.vpc_id

  ingress {
    description = "Allow HTTP from Anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow HTTPS from Anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    var.tags,
    local.module_tags,
    {
      Name = "Allow HTTP from Anywhere"
    },
  )
}

/*
 * Allow SSH from anywhere.
 */
resource "aws_security_group" "allow_ssh_from_anywhere" {
  /*
   * Only created if var.allow_ssh_from_anywhere is true.
   */
  count = var.allow_ssh_from_anywhere ? 1 : 0

  name_prefix = "allow_ssh_from_anywhere-"

  vpc_id = var.vpc_id

  ingress {
    description = "Allow SSH from Anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    var.tags,
    local.module_tags,
    {
      Name = "Allow SSH from Anywhere"
    },
  )
}
