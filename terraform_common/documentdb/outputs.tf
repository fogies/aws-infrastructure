/*
 * Admin user.
 */
output "admin_user" {
  value = local.resolved_admin_user
}

/*
 * Admin password.
 */
output "admin_password" {
  value = local.resolved_admin_password
  sensitive = true
}

/*
 * Cluster endpoint.
 */
output "endpoint" {
  value = local.resolved_endpoint
}

/*
 * List of hosts.
 */
output "hosts" {
  value = local.resolved_hosts
}

/*
 * Port on which to connect.
 */
output "port" {
  value = local.resolved_port
}
