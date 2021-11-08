/*
 * AWS Configuration.
 */
provider "aws" {
  profile = "aws-infrastructure"
  shared_credentials_file = "../secrets/aws/aws-infrastructure.credentials"

  region  = "us-east-1"
}
