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
BIN_TERRAFORM = './bin/terraform.exe'
DIR_TERRAFORM = './examples/codebuild'

BUILD_TIMESTAMP = datetime.now().strftime('%Y%m%d%H%M')


def codebuild_environment_variables_example_one(*, context):
    with examples.ecr.tasks.ecr_read_only(context=context) as ecr:
        return {
            'REGISTRY_URL': ecr.output.registry_url,
            'REPOSITORY': 'aws_infrastructure/example_one',
            'REPOSITORY_URL': ecr.output.repository_urls['aws_infrastructure/example_one'],
            'REPOSITORY_TAGS': 'testing latest {}'.format(BUILD_TIMESTAMP)
        }


def codebuild_environment_variables_example_two(*, context):
    with examples.ecr.tasks.ecr_read_only(context=context) as ecr:
        return {
            'REGISTRY_URL': ecr.output.registry_url,
            'REPOSITORY': 'aws_infrastructure/example_two',
            'REPOSITORY_URL': ecr.output.repository_urls['aws_infrastructure/example_two'],
            'REPOSITORY_TAGS': 'testing latest {}'.format(BUILD_TIMESTAMP)
        }


ns = Collection('codebuild')

ns_terraform = aws_infrastructure.tasks.library.codebuild.create_tasks(
    config_key=CONFIG_KEY,
    bin_terraform=BIN_TERRAFORM,
    dir_terraform=DIR_TERRAFORM,
    instances=['example_one', 'example_two'],
    codebuild_environment_variables={
        'example_one': codebuild_environment_variables_example_one,
        'example_two': codebuild_environment_variables_example_two,
    }
)

compose_collection(
    ns,
    ns_terraform,
    sub=False,
    exclude=aws_infrastructure.tasks.library.terraform.exclude_destroy_without_state(
        dir_terraform=DIR_TERRAFORM,
        exclude=[
            'init',
            'apply',
        ],
    )
)
