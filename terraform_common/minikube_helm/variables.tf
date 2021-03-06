/*
 * Availability zone in which to create instance.
 */
variable "aws_availability_zone" {
  # Typical value is "us-east-1a"

  type = string
}

/*
 * Architecture of the AMI to use, must correspond to instance type.
 */
variable "ami_architecture" {
  # Valid value is "amd64"
  # TODO: "arm64" not supported pending Minikube docker driver
  #       https://minikube.sigs.k8s.io/docs/drivers/docker/

  type = string
}

/*
 * Instance type to create.
 */
variable "aws_instance_type" {
  # Appropriate values are "t3.medium" (amd64) or larger
  # Must correspond to vars.source_ami_filter_architecture
  # Values with less than 4g of memory (i.e., "medium") cause Minikube configuration failures
  #
  # TODO: "arm64" not supported pending Minikube docker driver
  #       https://minikube.sigs.k8s.io/docs/drivers/docker/

  type = string
}

/*
 * True if providing an EIP to associate, False if module should create public IP.
 */
variable "eip" {
  type = bool
}

/*
 * Optional ID of Elastic IP to associate.
 */
variable "eip_id" {
  default = null

  type = string
}

/*
 * Optional IP of Elastic IP to associate.
 */
variable "eip_public_ip" {
  default = null

  type = string
}

/*
 * Name for this instance.
 */
variable "instance_name" {
  type = string
}

/*
 * Directory in which to generate files for this instance.
 */
variable "instance_dir" {
  type = string
}

/*
 * Tags to apply to created resources.
 */
variable "tags" {
  type = map

  default = {
  }
}
