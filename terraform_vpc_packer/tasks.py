from collections import namedtuple
import task_templates

CONFIG_KEY = 'terraform_vpc_packer'

init = task_templates.terraform.template_init(
    config_key=CONFIG_KEY
)
apply = task_templates.terraform.template_apply(
    config_key=CONFIG_KEY,
    init=init
)
destroy = task_templates.terraform.template_destroy(
    config_key=CONFIG_KEY,
    init=init
)
output = task_templates.terraform.template_output(
    config_key=CONFIG_KEY,
    init=init,
    output_tuple_factory=namedtuple('terraform_vpc_packer', ['subnet_id', 'vpc_id'])
)

vpc_packer = task_templates.terraform.template_context_manager(
    init=init,
    apply=apply,
    output=output,
    destroy=destroy
)
