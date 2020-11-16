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
  instance_dir = "instance_1"
  tasks_config_context = "terraform_minikube_helm_example"

  aws_availability_zone = "us-east-1a"
  ami_architecture = "amd64"
  aws_instance_type = "t3.medium"

  eip = false

  tags = {
  }
}

/*
 * Instance of Minikube Helm.
 *
 * Associated with a provided elastic IP.
 */
resource "aws_eip" "ip" {
}

module "minikube_helm_instance_2" {
  source = "../terraform_common/minikube_helm"

  instance_name = "instance_2"
  instance_dir = "instance_2"
  tasks_config_context = "terraform_minikube_helm_example"

  aws_availability_zone = "us-east-1a"
  ami_architecture = "amd64"
  aws_instance_type = "t3.medium"

  eip = true
  eip_id = aws_eip.ip.id
  eip_public_ip = aws_eip.ip.public_ip

  tags = {
  }
}
