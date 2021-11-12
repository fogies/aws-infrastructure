/*
 * An example Docker CodeBuild.
 */
module "example_codebuild" {
  source = "../../../terraform_common/codebuild"

  name = "aws_infrastructure_example_codebuild"
  source_archive = var.source_archive
}
