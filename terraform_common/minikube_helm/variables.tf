/*
 * Name for this instance.
 */
variable "name" {
  type = string
}

variable "ami_configuration" {
  # Configuration of ami_minikube to use.
  #
  # Valid values are enumerated in ami_minikube.
  #
  # A corresponding value must be set for "aws_instance_type".

  type = string
}

variable "aws_instance_type" {
  # Instance type in which to run ami_minikube.
  #
  # Typical values are "t3.medium" (amd64) or larger.
  #
  # A corresponding value must be set for "ami_configuration".

  type = string
}

/*
 * Whether the module should create its own VPC.
 *
 * If false, must provide vpc_id, vpc_default_security_group_id, and subnet_id.
 * If true, must provide availability_zone.
 */
variable "create_vpc" {
  type = bool
  default = false
}

/*
 * If module creates VPC and subnet, availability zone in which to create instance.
 */
variable "availability_zone" {
  # Typical value is "us-east-1a"
  type = string
  default = null
}

/*
 * If VPC is provided, its ID.
 */
variable "vpc_id" {
  type = string
  default = null
}

/*
 * If VPC is provided, its default security group ID.
 */
variable "vpc_default_security_group_id" {
  type = string
  default = null
}

/*
 * If subnet is provided, its ID.
 */
variable "subnet_id" {
  type = string
  default = null
}

/*
 * Whether the module should create its own EIP.
 *
 * If false, must provide eip_id and eip_public_ip.
 */
variable "create_eip" {
  type = bool
  default = false
}

/*
 * If EIP is provided, its ID.
 */
variable "eip_id" {
  type = string
  default = null
}

/*
 * If EIP is provided, its public IP.
 */
variable "eip_public_ip" {
  type = string
  default = null
}
