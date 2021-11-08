/*
 * Domain name of the hosted zone (e.g., "uwscope.org").
 */
variable "name" {
  type = string
}

/*
 * List of address records to create in the zone.
 */
variable "address_records" {
  type = list(
    object({
      name = string,
      ip = string
    })
  )
}

/*
 * AWS provider information.
 *
 * Used by the module for CLI access in maintaining the hosted zone.
 */
variable "aws_provider" {
  type = object({
    profile = string
    shared_credentials_file = string
    region = string
  })

  default = null
}
