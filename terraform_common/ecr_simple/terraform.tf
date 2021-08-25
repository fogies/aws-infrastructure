/*
 * Simple ECR.
 */

/*
 * The ECR.
 */
resource "aws_ecr_repository" "ecr" {
  for_each = var.names

  name = each.value
}
