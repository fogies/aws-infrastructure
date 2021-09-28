/*
 * Tag created resources.
 */
locals {
  tags = {
    "aws-infrastructure/examples/minikube": ""
  }
}

/*
 * Instance of Minikube Helm.
 */
module "minikube_instance" {
  source = "../../terraform_common/minikube_instance"

  name = "instance"

  ami_configuration = "amd64-medium"
  aws_instance_type = "t3.medium"

  create_vpc = true
  availability_zone = "us-east-1a"

  create_eip = true

  tags = local.tags
}
