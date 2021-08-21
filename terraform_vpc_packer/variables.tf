/*
 * Variables defining AWS basics.
 */

variable "aws_availability_zone" {
  default = "us-east-1a"
}

/*
 * Tags to apply to created resources.
 */
variable "tags" {
  type = map

  default = {
  }
}
