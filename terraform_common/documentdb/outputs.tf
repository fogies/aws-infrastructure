/*
 * Admin user.
 */
output "admin_user" {
  value = aws_docdb_cluster.docdb.master_username
}

/*
 * Admin password.
 */
output "admin_password" {
  value = aws_docdb_cluster.docdb.master_password
  sensitive = true
}

/*
 * Cluster endpoint.
 */
output "endpoint" {
  value = aws_docdb_cluster.docdb.endpoint
}

/*
 * List of hosts.
 */
output "hosts" {
  value = [ for instance_current in aws_docdb_cluster_instance.instances: instance_current.endpoint ]
}
