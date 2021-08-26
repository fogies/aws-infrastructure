/*
 * A first example CodeBuild in Docker.
 */
module "codebuild_source_one" {
  source = "../../terraform_common/codebuild"

  name = "example_one"
}

/*
 * A second example CodeBuild in Docker.
 */
module "codebuild_source_two" {
  source = "../../terraform_common/codebuild"

  name = "example_two"
}
