/*
 * IP to provide to instance of Minikube Helm.
 */
resource "aws_eip" "ip" {
}

/*
 * Instance of Minikube Helm.
 */
module "minikube_helm_instance" {
  source = "../../terraform_common/minikube_helm"

  name = "instance"

  aws_availability_zone = "us-east-1a"
  aws_instance_type = "t3.medium"

  ami_configuration = "amd64-medium"

  eip = true
  eip_id = aws_eip.ip.id
  eip_public_ip = aws_eip.ip.public_ip

  tags = {
  }
}
