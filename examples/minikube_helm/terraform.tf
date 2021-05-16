/*
 * Explicit configuration of providers.
 */
terraform {
  required_providers {
  }
}

/*
 * Instance of Minikube Helm.
 *
 * Associated with a provided elastic IP.
 */
resource "aws_eip" "ip" {
}

module "minikube_helm_instance" {
  source = "../../terraform_common/minikube_helm"

  instance_name = "instance"
  instance_dir = "instance"

  aws_availability_zone = "us-east-1a"
  aws_instance_type = "t3.medium"

  ami_configuration = "amd64-medium"

  eip = true
  eip_id = aws_eip.ip.id
  eip_public_ip = aws_eip.ip.public_ip

  tags = {
  }
}
