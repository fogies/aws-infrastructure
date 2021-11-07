/*
 * Tag created resources.
 */
locals {
  tags = {
    "aws-infrastructure/examples/minikube_multiple": ""
  }
}

/*
 * Multi-zone VPC in which to create instances.
 */
module "vpc" {
  source = "../../terraform_common/vpc"

  availability_zones = [
    "us-east-1a",
    "us-east-1b",
    "us-east-1c",
    "us-east-1d",
    # "us-east-1e", # Does not support t3.medium
    "us-east-1f",
  ]

  tags = local.tags
}

/*
 * IP to provide to amd64-medium.
 */
resource "aws_eip" "ip_amd64_medium" {
  tags = local.tags
}

/*
 * Randomly choose a subnet for amd64-medium.
 */
resource "random_shuffle" "subnet_id_amd64_medium" {
  input = module.vpc.subnet_ids
  result_count = 1
}

/*
 * Minikube AMI for amd64-medium.
 */
module "minikube_ami_amd64_medium" {
  source = "../../terraform_common/minikube_ami"

  owner_id = "732463742817"
  instance_type = "t3.medium"
  docker_volume_size = "20"
  build_timestamp = "20211107142725"
}

/*
 * Instance amd64-medium, in us-east-1a.
 */
module "minikube_instance_amd64_medium" {
  source = "../../terraform_common/minikube_instance"

  name = "amd64_medium"

  ami_id = module.minikube_ami_amd64_medium.id
  aws_instance_type = "t3.medium"

  vpc_id = module.vpc.vpc_id
  vpc_default_security_group_id = module.vpc.default_security_group_id
  subnet_id = one(random_shuffle.subnet_id_amd64_medium.result)

  eip_id = aws_eip.ip_amd64_medium.id
  eip_public_ip = aws_eip.ip_amd64_medium.public_ip

  tags = local.tags
}

/*
 * IP to provide to amd64-large.
 */
resource "aws_eip" "ip_amd64_large" {
  tags = local.tags
}

/*
 * Randomly choose a subnet for amd64-large.
 */
resource "random_shuffle" "subnet_id_amd64_large" {
  input = module.vpc.subnet_ids
  result_count = 1
}

/*
 * Minikube AMI for amd64-large.
 */
module "minikube_ami_amd64_large" {
  source = "../../terraform_common/minikube_ami"

  owner_id = "732463742817"
  instance_type = "t3.large"
  docker_volume_size = "20"
  build_timestamp = "20211107142725"
}

/*
 * Instance amd64-large, in us-east-1b.
 */
module "minikube_instance_amd64_large" {
  source = "../../terraform_common/minikube_instance"

  name = "amd64_large"

  ami_id = module.minikube_ami_amd64_large.id
  aws_instance_type = "t3.large"

  vpc_id = module.vpc.vpc_id
  vpc_default_security_group_id = module.vpc.default_security_group_id
  subnet_id = one(random_shuffle.subnet_id_amd64_large.result)

  eip_id = aws_eip.ip_amd64_large.id
  eip_public_ip = aws_eip.ip_amd64_large.public_ip

  tags = local.tags
}
