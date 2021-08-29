/*
 * Default availability zone.
 *
 * Output subnet_id will be set to the value for this availability_zone.
 */
variable "availability_zone" {
  type = string
  default = null
}

/*
 * Availability zones in which to create subnets.
 */
variable "availability_zones" {
  type = set(string)
  default = []
}

/*
 * Whether to assign a public IP to created instances.
 */
variable "map_public_ip_on_launch" {
  type = bool
  default = false
}
