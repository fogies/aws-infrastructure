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
 * An identify file for SSH access.
 */
locals {
  instance_key_private_filename = format(
    "id_rsa_%s",
    replace(
      local.resolved_public_ip, ".", "_"
    )
  )
}

resource "local_file" "instance_key_private" {
  filename = format(
    "%s/%s",
    var.name,
    local.instance_key_private_filename
  )

  sensitive_content = tls_private_key.instance_key_pair.private_key_pem
}

/*
 * A configuration file to be loaded by Python tasks.
 */
resource "local_file" "python_config" {
  filename = format(
    "%s/%s",
    var.name,
    "config.yaml"
  )

  content = templatefile(
    "${path.module}/templates/config.yaml.tmpl",
    {
        instance_name = var.name,
        instance_ip = local.resolved_public_ip
        instance_user = "ubuntu"
        instance_key = tls_private_key.instance_key_pair.private_key_pem
        instance_key_file = local.instance_key_private_filename
    }
  )
}
