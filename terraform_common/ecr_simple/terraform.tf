/*
 * Simple ECR.
 */

/*
 * The ECR.
 */
resource "aws_ecr_repository" "ecr" {
  name = var.name
}
