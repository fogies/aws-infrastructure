/*
 * Variables defining AWS basics.
 */

variable "aws_profile" {
  default = "default"
}

variable "aws_region" {
  default = "us-east-1"
}

variable "aws_availability_zone" {
  default = "us-east-1a"
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
  type = string
}

/*
 * Name for this instance of Minikube Helm.
 */
variable "instance_name" {
  type = string
}

/*
 * For created tasks, existing context within task hierarchy.
 */
variable "tasks_config_context" {
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
