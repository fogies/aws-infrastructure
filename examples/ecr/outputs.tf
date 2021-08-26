/*
 * URL of the registry containing the repositories.
 */
output "registry_url" {
  value = module.ecr.registry_url
}

/*
 * URLs of the repositories.
 */
output "repository_urls" {
  value = module.ecr.repository_urls
}
