"""
Tasks for managing the VPC for Packer.

Primarily intended for use through the context manager vpc_packer.
"""

from collections import namedtuple
from invoke import Collection

from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.terraform

# Key for configuration
CONFIG_KEY = 'terraform_vpc_packer'

# Configure a collection
ns = Collection('terraform-vpc-packer')

ns.configure({
    CONFIG_KEY: {
        'working_dir': 'terraform_vpc_packer',
        'bin_dir': '../bin'
    }
})

# Define and import tasks
ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
    config_key=CONFIG_KEY,
    output_tuple_factory=namedtuple('terraform_vpc_packer', ['subnet_id', 'vpc_id'])
)

# Compose the collection
#
# Does not expose any of the tasks, could be modified for debugging.
compose_collection(
    ns,
    ns_terraform,
    sub=False,
    include=[]
)

# A context manager
vpc_packer = aws_infrastructure.tasks.library.terraform.create_context_manager(
    init=ns_terraform.tasks.init,
    apply=ns_terraform.tasks.apply,
    output=ns_terraform.tasks.output,
    destroy=ns_terraform.tasks.destroy
)
