/*
 * Tag created resources.
 */
locals {
  tags = {
    "aws-infrastructure/examples/documentdb": ""
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
 * A random password for the admin account.
 */
resource "random_password" "admin_password" {
  length           = 32
  special          = false
}

/*
 * Instance of DocumentDB.
 */
module "documentdb" {
  source = "../../terraform_common/documentdb"

  name = "examples-documentdb"

  apply_immediately = true

  admin_user = "examples_documentdb_admin"
  admin_password = random_password.admin_password.result

  deletion_protection = false

  instance_count = 1
  instance_class = "db.t3.medium"
  subnet_ids = module.vpc.subnet_ids

  tags = local.tags
}

/*
 * Instance of Minikube Helm.
 */
module "minikube_instance" {
  source = "../../terraform_common/minikube_instance"

  name = "instance"

  ami_configuration = "amd64-medium"
  aws_instance_type = "t3.medium"

  vpc_id = module.vpc.vpc_id
  vpc_default_security_group_id = module.vpc.default_security_group_id
  subnet_id = module.vpc.subnet_id

  create_eip = true

  tags = local.tags
}
