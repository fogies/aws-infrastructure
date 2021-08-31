from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.eip
import aws_infrastructure.tasks.library.terraform
from invoke import Collection

CONFIG_KEY = 'examples_eip'
BIN_TERRAFORM = './bin/terraform.exe'
DIR_TERRAFORM = './examples/eip'

ns = Collection('eip')

ns_eip = aws_infrastructure.tasks.library.eip.create_tasks(
    config_key=CONFIG_KEY,
    bin_terraform=BIN_TERRAFORM,
    dir_terraform=DIR_TERRAFORM,
)

compose_collection(
    ns,
    ns_eip,
    sub=False,
    exclude=aws_infrastructure.tasks.library.terraform.exclude_destroy_without_state(
        dir_terraform=DIR_TERRAFORM,
        exclude=[
            'init',
            'output',
        ],
    )
)

eip_read_only = aws_infrastructure.tasks.library.eip.create_eip_read_only(
    ns_eip=ns_eip
)
