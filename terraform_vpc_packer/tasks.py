from invoke import Collection
from collections import namedtuple
import aws_infrastructure.task_templates

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

init = aws_infrastructure.task_templates.terraform.task_init(
    config_key=CONFIG_KEY
)
apply = aws_infrastructure.task_templates.terraform.task_apply(
    config_key=CONFIG_KEY,
    init=init
)
destroy = aws_infrastructure.task_templates.terraform.task_destroy(
    config_key=CONFIG_KEY,
    init=init
)
output = aws_infrastructure.task_templates.terraform.task_output(
    config_key=CONFIG_KEY,
    init=init,
    output_tuple_factory=namedtuple('terraform_vpc_packer', ['subnet_id', 'vpc_id'])
)

# Add tasks to collection
ns.add_task(apply)
ns.add_task(destroy)
ns.add_task(output)

# A context manager
vpc_packer = aws_infrastructure.task_templates.terraform.template_context_manager(
    init=init,
    apply=apply,
    output=output,
    destroy=destroy
)
