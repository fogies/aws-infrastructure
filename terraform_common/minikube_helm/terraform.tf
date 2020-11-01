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
 * - Generate a random minikube_id to include in tags.
 */
resource "random_uuid" "minikube_id" {
}

locals {
  minikube_id = format("minikube-%s", random_uuid.minikube_id.result)

  module_tags = {
    terraform   = true
    minikube_id = local.minikube_id
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
  source = "../vpc_simple"

  aws_availability_zone = var.aws_availability_zone

  # Require instances to indicate if they want a public IP.
  map_public_ip_on_launch = false

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

  ami_architecture = var.ami_architecture
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
  availability_zone = var.aws_availability_zone

  vpc_security_group_ids = module.instance_security_groups.security_group_ids

  key_name = aws_key_pair.instance_key_pair.id

  associate_public_ip_address = true

  tags = merge(
    var.tags,
    local.module_tags,
    {
    },
  )
}

/*
 * Create and ignore a .minikube_helm directory with created state.
 */
resource "local_file" "gitignore" {
  filename = format(
    "%s/%s",
    var.instance_name,
    ".gitignore"
  )

  content = <<-EOT
    /*
  EOT
}

/*
 * An identify file for SSH access.
 */
resource "local_file" "instance_key_private" {
  filename = format(
    "%s/id_rsa_%s",
    var.instance_name,
    replace(aws_instance.minikube.public_ip, ".", "_")
  )

  sensitive_content = tls_private_key.instance_key_pair.private_key_pem
}

/*
 * A set of tasks for interacting with the instance.
 */
resource "local_file" "python_tasks" {
  filename = format(
    "%s/%s",
    var.instance_name,
    "tasks.py"
  )

  content = templatefile(
    "${path.module}/templates/tasks.py.tmpl",
    {
        instance_name = var.instance_name,

        tasks_config_context = var.tasks_config_context,
    }
  )
}

resource "local_file" "python_init" {
  filename = format(
    "%s/%s",
    var.instance_name,
    "__init__.py"
  )

  content = templatefile(
    "${path.module}/templates/__init__.py.tmpl",
    {
        instance_name = var.instance_name,

        instance_ip = aws_instance.minikube.public_ip
        instance_identity_file = local_file.instance_key_private.filename
    }
  )
}
