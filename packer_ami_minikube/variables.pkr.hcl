variable "aws_region" {
  default = "us-east-1"
}

variable "aws_instance_type" {
  default = "t3.medium"
}

variable "source_ami_filter_owners" {
  # Filter to Ubuntu
  default = ["099720109477"]
}

variable "source_ami_filter_name" {
  # Filter to Ubuntu 20.04
  default = "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"

  # Filter to Ubuntu 20.04 Minimal
  # default = "ubuntu-minimal/images/hvm-ssd/ubuntu-focal-20.04-amd64-minimal-*"
}
