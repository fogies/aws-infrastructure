/*
 * An example Docker CodeBuild.
 */
module "example_codebuild" {
  source = "../../../terraform_common/codebuild"

  name = "example_codebuild"
  source_archive = var.source_archive
}
