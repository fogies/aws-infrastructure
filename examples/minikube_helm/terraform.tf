/*
 * Tag created resources.
 */
locals {
  tags = {
    "aws-infrastructure/examples/minikube_helm": ""
  }
}

/*
 * Instance of Minikube Helm.
 */
module "minikube_helm_instance" {
  source = "../../terraform_common/minikube_helm"

  name = "instance"

  ami_configuration = "amd64-medium"
  aws_instance_type = "t3.medium"

  create_vpc = true
  availability_zone = "us-east-1a"

  create_eip = true

  tags = local.tags
}
