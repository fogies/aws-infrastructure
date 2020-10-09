output "security_group_ids" {
  value = compact(list(
    var.allow_egress_to_anywhere ? aws_security_group.allow_egress_to_anywhere[0].id : 0,
    var.allow_egress_to_anywhere ? aws_security_group.allow_http_from_anywhere[0].id : 0,
    var.allow_egress_to_anywhere ? aws_security_group.allow_ssh_from_anywhere[0].id : 0,
  ))
}
