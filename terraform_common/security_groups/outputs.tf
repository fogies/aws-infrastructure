/*
 * List of IDs of created security groups.
 */
output "security_group_ids" {
  value = compact([
    var.allow_egress_to_anywhere ? one(aws_security_group.allow_egress_to_anywhere).id : null,
    var.allow_http_from_anywhere ? one(aws_security_group.allow_http_from_anywhere).id : null,
    var.allow_ssh_from_anywhere ? one(aws_security_group.allow_ssh_from_anywhere).id : null,
  ])
}
