/*
 * Instance of ECR Simple.
 */
module "ecr" {
  source = "../../terraform_common/ecr_simple"

  name = "example_ecr"
}
