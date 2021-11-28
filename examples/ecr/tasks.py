from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.ecr
import aws_infrastructure.tasks.library.terraform
from invoke import Collection

CONFIG_KEY = 'examples_ecr'
TERRAFORM_BIN = './bin/terraform.exe'
TERRAFORM_DIR = './examples/ecr'

ns = Collection('ecr')

ns_ecr = aws_infrastructure.tasks.library.ecr.create_tasks(
    config_key=CONFIG_KEY,
    terraform_bin=TERRAFORM_BIN,
    terraform_dir=TERRAFORM_DIR,
)

compose_collection(
    ns,
    ns_ecr,
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

ecr_read_only = aws_infrastructure.tasks.library.ecr.create_ecr_read_only(
    ns_ecr=ns_ecr
)
