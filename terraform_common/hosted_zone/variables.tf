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