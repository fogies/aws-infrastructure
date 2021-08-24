from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.ecr
import aws_infrastructure.tasks.library.terraform
from invoke import Collection

CONFIG_KEY = 'examples_ecr'
BIN_TERRAFORM = './bin/terraform.exe'
DIR_TERRAFORM = './examples/ecr'

ns = Collection('ecr')

ns_ecr = aws_infrastructure.tasks.library.ecr.create_tasks(
    config_key=CONFIG_KEY,
    bin_terraform=BIN_TERRAFORM,
    dir_terraform=DIR_TERRAFORM,
)

compose_collection(
    ns,
    ns_ecr,
    sub=False,
    exclude=aws_infrastructure.tasks.library.terraform.exclude_destroy_without_state(
        dir_terraform=DIR_TERRAFORM,
        exclude=[
            'init',
            'output',
        ],
    )
)

ecr_read_only = aws_infrastructure.tasks.library.ecr.create_ecr_read_only(
    ns_ecr=ns_ecr
)
