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

variable "aws_instance_type" {
  default = "t3.medium"
}

/*
 * Tags to apply to created resources.
 */
variable "tags" {
  type = map

  default = {
  }
}
