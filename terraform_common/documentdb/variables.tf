/*
 * Name of DocumentDB.
 */
variable "name" {
  type = string
}

/*
 * Admin account user.
 */
variable "admin_user" {
  type = string
}

/*
 * Admin account password.
 */
variable "admin_password" {
  type = string
}

/*
 * Type of instance to use for powering the database.
 */
variable "instance_class" {
  type = string
}

/*
 * Number of instances to use for powering the database.
 */
variable "instance_count" {
  type = number
}

/*
 * IDs of subnets in which to create instances.
 */
variable "subnet_ids" {
  type = list(string)
}
