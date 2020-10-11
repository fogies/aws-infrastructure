/*
 * Tags to apply to created resources.
 */
variable "tags" {
  type = map

  default = {
  }
}

/*
 * Availability zone to use.
 */
variable "aws_availability_zone" {
  type = string
}

/*
 * Whether to assign a public IP to created instances.
 */
variable "map_public_ip_on_launch" {
  type = bool
}
