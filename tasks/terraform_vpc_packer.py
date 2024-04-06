"""
Tasks for managing the VPC for Packer.

Primarily intended for use through the context manager vpc_packer.
"""

from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.terraform
from collections import namedtuple
from invoke import Collection

CONFIG_KEY = 'terraform_vpc_packer'
TERRAFORM_BIN = './bin/terraform.exe'
TERRAFORM_DIR = './terraform_vpc_packer'

ns = Collection('vpc-packer')

ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
    config_key=CONFIG_KEY,
    terraform_bin=TERRAFORM_BIN,
    terraform_dir=TERRAFORM_DIR,
    auto_approve=True,
    output_tuple_factory=namedtuple('terraform_vpc_packer', ['subnet_id', 'vpc_id'])
)

# Does not expose any of the tasks, could be modified for debugging.
compose_collection(
    ns,
    ns_terraform,
    sub=False,
    include=[
    ]
)

# A context manager
vpc_packer = aws_infrastructure.tasks.library.terraform.create_context_manager(
    init=ns_terraform.tasks.init,
    apply=ns_terraform.tasks.apply,
    output=ns_terraform.tasks.output,
    destroy=ns_terraform.tasks.destroy
)
