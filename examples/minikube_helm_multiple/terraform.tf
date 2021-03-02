/*
 * Explicit configuration of providers.
 */
terraform {
  required_providers {
  }
}

/*
 * Instance 1 of Minikube Helm.
 */
module "minikube_helm_instance_1" {
  source = "../../terraform_common/minikube_helm"

  instance_name = "instance_1"
  instance_dir = "instance_1"

  aws_availability_zone = "us-east-1a"
  ami_architecture = "amd64"
  aws_instance_type = "t3.medium"

  eip = false

  tags = {
  }
}

/*
 * Instance 2 of Minikube Helm.
 */
module "minikube_helm_instance_2" {
  source = "../../terraform_common/minikube_helm"

  instance_name = "instance_2"
  instance_dir = "instance_2"

  aws_availability_zone = "us-east-1a"
  ami_architecture = "amd64"
  aws_instance_type = "t3.medium"

  eip = false

  tags = {
  }
}

/*
 * Instance 3 of Minikube Helm.
 */
module "minikube_helm_instance_3" {
  source = "../../terraform_common/minikube_helm"

  instance_name = "instance_3"
  instance_dir = "instance_3"

  aws_availability_zone = "us-east-1a"
  ami_architecture = "amd64"
  aws_instance_type = "t3.medium"

  eip = false

  tags = {
  }
}
