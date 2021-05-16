/*
 * Explicit configuration of providers.
 */
terraform {
  required_providers {
  }
}

/*
 * Instance amd64-medium.
 */
module "minikube_helm_instance_amd64_medium" {
  source = "../../terraform_common/minikube_helm"

  instance_name = "amd64_medium"
  instance_dir = "amd64_medium"

  aws_availability_zone = "us-east-1a"
  aws_instance_type = "t3.medium"

  ami_configuration = "amd64-medium"

  eip = false

  tags = {
  }
}

/*
 * Instance amd64-large.
 */
module "minikube_helm_instance_amd64_large" {
  source = "../../terraform_common/minikube_helm"

  instance_name = "amd64_large"
  instance_dir = "amd64_large"

  aws_availability_zone = "us-east-1a"
  aws_instance_type = "t3.large"

  ami_configuration = "amd64-large"

  eip = false

  tags = {
  }
}
