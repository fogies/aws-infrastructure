/*
 * Explicit configuration of providers.
 */
terraform {
  required_providers {
  }
}

/*
 * Instance of Minikube Helm.
 */
module "minikube_helm_instance_1" {
  source = "../terraform_common/minikube_helm"

  instance_name = "instance_1"
  tasks_config_context = "terraform_minikube_helm_example"

  ami_architecture = "amd64"
  aws_instance_type = "t3.small"

  tags = {
  }
}

/*
 * Instance of Minikube Helm.
 */
module "minikube_helm_instance_2" {
  source = "../terraform_common/minikube_helm"

  instance_name = "instance_2"
  tasks_config_context = "terraform_minikube_helm_example"

  ami_architecture = "amd64"
  aws_instance_type = "t3.small"

  tags = {
  }
}
