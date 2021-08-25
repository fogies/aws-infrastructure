/*
 * URLs of the ECRs.
 */
output "repository_urls" {
  value = tomap({
    for name, ecr in aws_ecr_repository.ecr : name => ecr.repository_url
  })
}
