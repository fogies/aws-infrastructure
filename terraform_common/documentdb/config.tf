/*
 * Create an instance directory for config.yaml and related files.
 *
 * Place a .gitignore in that directory to ensure we do not commit.
 */
resource "local_file" "gitignore" {
  filename = format(
    "%s/%s",
    var.name,
    ".gitignore"
  )

  content = <<-EOT
    /*
  EOT
}

/*
 * A configuration file to be loaded by Python tasks.
 */
resource "local_file" "documentdb_config" {
  filename = format(
    "%s/%s",
    var.name,
    "documentdb_config.yaml"
  )

  content = yamlencode({
    admin_user = local.resolved_admin_user
    admin_password = local.resolved_admin_password
    endpoint = local.resolved_endpoint
    hosts = local.resolved_hosts
  })
}
