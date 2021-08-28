/*
 * Availability zone in which to create instance.
 */
variable "aws_availability_zone" {
  # Typical value is "us-east-1a"

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
variable "name" {
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
