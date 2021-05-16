#
# Variables describing the VPC in which Packer executes.
#

variable "vpc_packer_vpc_id" {
  type = string
}

variable "vpc_packer_subnet_id" {
  type = string
}
