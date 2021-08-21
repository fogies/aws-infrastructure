from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.ecr_simple
from invoke import Collection

CONFIG_KEY = 'examples_ecr'
BIN_TERRAFORM = './bin/terraform.exe'
DIR_TERRAFORM = './examples/ecr'

ns = Collection('ecr')

ns_ecr = aws_infrastructure.tasks.library.ecr_simple.create_tasks(
    config_key=CONFIG_KEY,
    bin_terraform=BIN_TERRAFORM,
    dir_terraform=DIR_TERRAFORM,
)

compose_collection(
    ns,
    ns_ecr,
    sub=False,
    include=['apply', 'destroy'],
)

ecr_read_only = aws_infrastructure.tasks.library.ecr_simple.create_ecr_read_only(
    ns_ecr=ns_ecr
)
