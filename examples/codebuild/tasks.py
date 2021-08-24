"""
Exploratory task for CodeBuild.
"""

from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.codebuild
import aws_infrastructure.tasks.library.terraform
from invoke import Collection

CONFIG_KEY = 'codebuild'
BIN_TERRAFORM = './bin/terraform.exe'
DIR_TERRAFORM = './examples/codebuild'

ns = Collection('codebuild')

ns_terraform = aws_infrastructure.tasks.library.codebuild.create_tasks(
    config_key=CONFIG_KEY,
    bin_terraform=BIN_TERRAFORM,
    dir_terraform=DIR_TERRAFORM,
    instances=['example_one', 'example_two']
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
