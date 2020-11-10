variable "aws_region" {
  default = "us-east-1"
}

variable "aws_instance_type" {
  # Appropriate values are "t3.medium" (amd64) or larger
  # Must correspond to vars.source_ami_filter_architecture
  # Values with less than 4g of memory (i.e., "medium") cause Minikube configuration failures
  #
  # TODO: "arm64" not supported pending Minikube docker driver
  #       https://minikube.sigs.k8s.io/docs/drivers/docker/

  type = string
}

variable "ami_architecture" {
  # Valid value is "amd64"
  # TODO: "arm64" not supported pending Minikube docker driver
  #       https://minikube.sigs.k8s.io/docs/drivers/docker/

  type = string
}

locals {
  # Timestamp of this build
  timestamp = "{{timestamp}}"

  # Filter to AMI owned by the Ubuntu ID
  source_ami_filter_owners = ["099720109477"]

  # Filter to the name of the source AMI. Examples of names:
  #
  # Ubuntu 20.04 for amd64 architecture
  # - "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"
  #
  # Ubuntu 20.04 for amd64 architecture
  # - "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-arm64-server-*"
  #
  # Ubuntu Minimal 20.04 for amd64 architecture
  # - "ubuntu-minimal/images/hvm-ssd/ubuntu-focal-20.04-amd64-minimal-*"
  #
  # Derive from variable ami_architecture
  source_ami_filter_name = format(
    "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-%s-server-*",
    var.ami_architecture
  )

  # Name of the created AMI, derive from variable ami_architecture
  ami_name = format(
    "minikube-%s-%s",
    var.ami_architecture,
    local.timestamp
  )
}
