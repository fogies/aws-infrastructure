from collections import namedtuple

import aws_infrastructure.task_templates.terraform
from invoke import Collection

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
terraform_tasks = aws_infrastructure.task_templates.terraform.create_tasks(
    config_key=CONFIG_KEY,
    output_tuple_factory=namedtuple('terraform_vpc_packer', ['subnet_id', 'vpc_id'])
)


# Add tasks to our collection
# - Exclude for legibility, could be enabled for debugging.
# for task_current in terraform_tasks.values():
#     ns.add_task(task_current)


# A context manager
vpc_packer = aws_infrastructure.task_templates.terraform.create_context_manager(
    init=terraform_tasks.tasks.init,
    apply=terraform_tasks.tasks.apply,
    output=terraform_tasks.tasks.output,
    destroy=terraform_tasks.tasks.destroy
)
