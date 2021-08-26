/*
 * Instance of ECR Simple.
 */
module "ecr" {
  source = "../../terraform_common/ecr_simple"

  names = [
    "aws_infrastructure/example_one",
    "aws_infrastructure/example_two",
  ]
}
