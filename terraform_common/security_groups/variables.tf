variable "vpc_id" {
  type = string
}

variable "allow_egress_to_anywhere" {
  type    = bool
  default = false
}

variable "allow_http_from_anywhere" {
  type    = bool
  default = false
}

variable "allow_ssh_from_anywhere" {
  type    = bool
  default = false
}

/*
 * Tags to apply to created resources.
 */
variable "tags" {
  type = map

  default = {
  }
}
