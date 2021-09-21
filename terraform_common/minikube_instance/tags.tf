/*
 * Variable for tags to apply to created resources.
 */
variable "tags" {
  type = map

  default = {
  }
}

/*
 * Combine provided tags with any local tags.
 */
locals {
  module_tags = merge(
    var.tags,
    {
    }
  )
}
