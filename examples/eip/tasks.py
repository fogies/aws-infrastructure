from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.eip
import aws_infrastructure.tasks.library.terraform
from invoke import Collection

CONFIG_KEY = 'examples_eip'
TERRAFORM_BIN = './bin/terraform.exe'
TERRAFORM_DIR = './examples/eip'

ns = Collection('eip')

ns_eip = aws_infrastructure.tasks.library.eip.create_tasks(
    config_key=CONFIG_KEY,
    terraform_bin=TERRAFORM_BIN,
    terraform_dir=TERRAFORM_DIR,
)

compose_collection(
    ns,
    ns_eip,
    sub=False,
    exclude=aws_infrastructure.tasks.library.terraform.exclude_without_state(
        terraform_dir=TERRAFORM_DIR,
        exclude=[
            'init',
            'output',
        ],
        exclude_without_state=[
            'destroy'
        ],
    )
)

eip_read_only = aws_infrastructure.tasks.library.eip.create_eip_read_only(
    ns_eip=ns_eip
)
