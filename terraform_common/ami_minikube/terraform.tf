/*
 * AMI for Minikube.
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
 * Locals that define our AMI.
 */
locals {
  # ID of our AWS Probe Account
  # TODO: Replace with whatever account actually hosts these
  ami_minikube_owner_id = "732463742817"

  # Name by which to filter the AMI
  ami_minikube_filter_name = format(
    "minikube-%s-*",
    var.configuration
  )
}

/*
 * AMI for the latest build of Minikube.
 */
data "aws_ami" "minikube" {
  owners = [local.ami_minikube_owner_id]

  most_recent = true
  filter {
    name   = "name"
    values = [local.ami_minikube_filter_name]
  }
}
