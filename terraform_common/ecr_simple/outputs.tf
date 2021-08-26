/*
 * URL of the registry containing the repositories.
 */
output "registry_url" {
  value = split("/", aws_ecr_repository.ecr[tolist(var.names)[0]].repository_url)[0]
}

/*
 * URLs of the repositories.
 */
output "repository_urls" {
  value = tomap({
    for name, ecr in aws_ecr_repository.ecr : name => ecr.repository_url
  })
}
