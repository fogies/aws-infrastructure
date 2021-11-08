/*
 * Locals that define our AMI.
 */
locals {
  architecture = {
    "t3.medium"="amd64",
    "t3.large"="amd64",
  }[var.instance_type]

  instance_size = {
    "t3.medium"="medium",
    "t3.large"="large",
  }[var.instance_type]

  # Name by which to identify the AMI
  ami_name = format(
    "minikube-%s-%s-%s-%s",
    local.architecture,
    local.instance_size,
    format("%sgb", var.docker_volume_size),
    var.build_timestamp,
  )
}

/*
 * AMI for the desired build of Minikube.
 */
data "aws_ami" "minikube" {
  owners = [var.owner_id]

  filter {
    name   = "name"
    values = [local.ami_name]
  }
}
