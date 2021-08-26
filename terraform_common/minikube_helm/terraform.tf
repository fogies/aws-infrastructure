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
 * Tags to apply to created resources.
 */
locals {
  module_tags = {
    terraform   = true
    minikube_id = local.minikube_id
  }
}

/*
 * Generate a random minikube_id to include in tags.
 */
resource "random_uuid" "minikube_id" {
}

locals {
  minikube_id = format("minikube-%s", random_uuid.minikube_id.result)
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
  availability_zone = var.aws_availability_zone

  vpc_security_group_ids = module.instance_security_groups.security_group_ids

  key_name = aws_key_pair.instance_key_pair.id

  tags = merge(
    var.tags,
    local.module_tags,
    {
    },
  )
}

/*
 * If we were not provided an elastic IP, create our own.
 */
resource "aws_eip" "eip" {
  count = var.eip ? 0 : 1
}

/*
 * Associate to our elastic IP, either as provided or as created.
 */
resource "aws_eip_association" "eip_association" {
  instance_id = aws_instance.minikube.id
  allocation_id = var.eip ? var.eip_id : aws_eip.eip[0].id
}

/*
 * Our public IP is based on how we associated an EIP.
 */
locals {
  instance_public_ip = var.eip ? var.eip_public_ip : aws_eip.eip[0].public_ip
}

/*
 * Create and ignore a directory with created state.
 */
resource "local_file" "gitignore" {
  filename = format(
    "%s/%s",
    var.name,
    ".gitignore"
  )

  content = <<-EOT
    /*
  EOT
}

/*
 * An identify file for SSH access.
 */
locals {
  instance_key_private_filename = format(
    "id_rsa_%s",
    replace(
      local.instance_public_ip, ".", "_"
    )
  )
}

resource "local_file" "instance_key_private" {
  filename = format(
    "%s/%s",
    var.name,
    local.instance_key_private_filename
  )

  sensitive_content = tls_private_key.instance_key_pair.private_key_pem
}

/*
 * A configuration file to be loaded by Python tasks.
 */
resource "local_file" "python_config" {
  filename = format(
    "%s/%s",
    var.name,
    "config.yaml"
  )

  content = templatefile(
    "${path.module}/templates/config.yaml.tmpl",
    {
        instance_name = var.name,
        instance_ip = local.instance_public_ip
        instance_user = "ubuntu"
        instance_key = tls_private_key.instance_key_pair.private_key_pem
        instance_key_file = local.instance_key_private_filename
    }
  )
}
