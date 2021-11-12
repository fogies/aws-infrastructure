/*
 * Instance of ECR Simple.
 */
module "ecr" {
  source = "../../terraform_common/ecr"

  names = [
    "aws_infrastructure/example_codebuild",
  ]
}
