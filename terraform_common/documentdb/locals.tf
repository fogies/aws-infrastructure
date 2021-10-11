/*
 * Resolve variables that are in both the config.yaml and module outputs.
 */
locals {
  resolved_admin_user = aws_docdb_cluster.docdb.master_username
  resolved_admin_password = aws_docdb_cluster.docdb.master_password
  resolved_endpoint = aws_docdb_cluster.docdb.endpoint
  resolved_hosts = [ for instance_current in aws_docdb_cluster_instance.instances: instance_current.endpoint ]
}
