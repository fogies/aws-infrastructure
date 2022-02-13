/*
 * Tag created resources.
 */
locals {
  tags = {
    "aws-infrastructure/examples/minikube": ""
  }
}

/*
 * ID of the Minikube AMI.
 */
module "minikube_ami" {
  source = "../../terraform_common/minikube_ami"

  owner_id = "732463742817"
  instance_type = "t3.large"
  docker_volume_size = "25"
  build_timestamp = "20220213214320"
}

/*
 * Instance of Minikube.
 */
module "minikube_instance" {
  source = "../../terraform_common/minikube_instance"

  name = "instance"

  ami_id = module.minikube_ami.id
  aws_instance_type = "t3.large"

  create_vpc = true
  availability_zone = "us-east-1a"

  create_eip = true

  tags = local.tags
}
