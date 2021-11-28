"""
Tasks for managing the Minikube AMI.
"""

from invoke import Collection
from invoke import task
import json
import os
import tasks.terraform_vpc_packer

from packer_ami_minikube.config import BUILD_CONFIG

CONFIG_KEY = 'minikube_ami'
PACKER_BIN = './bin/packer.exe'
PACKER_DIR = './packer_ami_minikube'

ns = Collection('ami-minikube')


@task
def build(context):
    """
    Build the Minikube AMI.
    """

    with tasks.terraform_vpc_packer.vpc_packer(context=context) as vpc_packer:
        vpc_packer_output = vpc_packer.output

        with context.cd(PACKER_DIR):
            print('Building AMI Minikube')

            # Build each configuration in BUILD_CONFIG
            for build_config_name, build_config in BUILD_CONFIG.items():
                context.run(
                    command=' '.join([
                        os.path.relpath(PACKER_BIN, PACKER_DIR),
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


# Compose the collection
ns.add_task(build)
