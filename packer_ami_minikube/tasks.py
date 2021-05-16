from invoke import Collection
from invoke import task
import json
from pathlib import Path
import terraform_vpc_packer.tasks

from .config import BUILD_CONFIG

# Key for configuration
INVOKE_CONFIG_KEY = 'packer_ami_minikube'

# Configure a collection
ns = Collection('ami-minikube')

ns.configure({
    INVOKE_CONFIG_KEY: {
        'working_dir': 'packer_ami_minikube',
        'bin_dir': '../bin'
    }
})


# Define and import tasks
@task
def build(context):
    """
    Build the AMI.
    """

    invoke_config = context.config[INVOKE_CONFIG_KEY]
    working_dir = Path(invoke_config.working_dir)
    bin_packer = Path(invoke_config.bin_dir, 'packer.exe')

    with terraform_vpc_packer.tasks.vpc_packer(context=context) as vpc_packer:
        vpc_packer_output = vpc_packer.output

        with context.cd(working_dir):
            print('Building AMI Minikube')

            # Build each configuration in BUILD_CONFIG
            for build_config_name, build_config in BUILD_CONFIG.items():
                context.run(
                    command=' '.join([
                        '{}'.format(bin_packer),
                        'build',
                        '-color=false',
                        '-var vpc_packer_vpc_id={}'.format(vpc_packer_output.vpc_id),
                        '-var vpc_packer_subnet_id={}'.format(vpc_packer_output.subnet_id),
                        ' '.join([
                            '-var {}={}'.format(build_config_key, json.dumps(build_config_value))
                            for build_config_key, build_config_value
                            in build_config.items()
                        ]),
                        '.'
                    ]),
                )


# Add tasks to our collection
ns.add_task(build)
