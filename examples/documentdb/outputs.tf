/*
 * Admin user.
 */
output "admin_user" {
  value = module.documentdb.admin_user
}

/*
 * Admin password.
 */
output "admin_password" {
  value = module.documentdb.admin_password
  sensitive = true
}

/*
 * Cluster endpoint.
 */
output "endpoint" {
  value = module.documentdb.endpoint
}

/*
 * List of hosts.
 */
output "hosts" {
  value = module.documentdb.hosts
}

/*
 * Port on which to connect.
 */
output "port" {
  value = module.documentdb.port
}
