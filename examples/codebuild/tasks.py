"""
Exploratory task for CodeBuild.
"""

from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.codebuild
import aws_infrastructure.tasks.library.terraform
from datetime import datetime
import examples.ecr.tasks
from invoke import Collection

CONFIG_KEY = 'codebuild'
TERRAFORM_BIN = './bin/terraform.exe'
TERRAFORM_DIR = './examples/codebuild/terraform'
STAGING_LOCAL_DIR = './.staging/codebuild/example_codebuild'
AWS_PROFILE = 'aws-infrastructure'
AWS_SHARED_CREDENTIALS_PATH = './secrets/aws/aws-infrastructure.credentials'

SOURCE_DIR = './examples/docker/example_codebuild'
CODEBUILD_PROJECT_NAME = 'aws_infrastructure_example_codebuild'

BUILD_TIMESTAMP = datetime.now().strftime('%Y%m%d%H%M')


def codebuild_environment_variables_factory(*, context):
    with examples.ecr.tasks.ecr_read_only(context=context) as ecr:
        return {
            'REGISTRY_URL': ecr.output.registry_url,
            'REPOSITORY': 'aws_infrastructure/example_codebuild',
            'REPOSITORY_URL': ecr.output.repository_urls['aws_infrastructure/example_codebuild'],
            'REPOSITORY_TAGS': 'latest {}'.format(BUILD_TIMESTAMP)
        }


ns = Collection('codebuild')

ns_terraform = aws_infrastructure.tasks.library.codebuild.create_tasks(
    config_key=CONFIG_KEY,
    terraform_bin=TERRAFORM_BIN,
    terraform_dir=TERRAFORM_DIR,
    staging_local_dir=STAGING_LOCAL_DIR,
    aws_profile=AWS_PROFILE,
    aws_shared_credentials_path=AWS_SHARED_CREDENTIALS_PATH,
    source_dir=SOURCE_DIR,
    codebuild_project_name=CODEBUILD_PROJECT_NAME,
    codebuild_environment_variables_factory=codebuild_environment_variables_factory,
)

compose_collection(
    ns,
    ns_terraform,
    sub=False,
    exclude=aws_infrastructure.tasks.library.terraform.exclude_without_state(
        terraform_dir=TERRAFORM_DIR,
        exclude=[
        ],
        exclude_without_state=[
            'destroy'
        ],
    )
)
