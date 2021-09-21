from invoke import Collection
from invoke import task
import os
from pathlib import Path
import re
import ruamel.yaml
import semver
from typing import List
from typing import Union

import aws_infrastructure.tasks.library.instance_helm
import aws_infrastructure.tasks.library.instance_helmfile
import aws_infrastructure.tasks.library.instance_ssh


def _task_ip(
    *,
    config_key: str,
    instance_config
):
    @task
    def ip(context):
        """
        Print the public IP of the instance.
        """
        print(instance_config['instance_ip'])

    return ip


def create_tasks(
    *,
    config_key: str,
    dir_terraform: Union[Path, str],
    dir_helm_repo: Union[Path, str],
    instance: str,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    dir_terraform = Path(dir_terraform)
    dir_instance = Path(dir_terraform, instance)
    dir_helm_repo = Path(dir_helm_repo)

    path_config = Path(dir_instance, 'config.yaml')
    with open(path_config) as file_config:
        yaml_config = ruamel.yaml.safe_load(file_config)

    instance_name = yaml_config['instance_name']

    ns = Collection(instance_name)

    ssh = aws_infrastructure.tasks.library.instance_ssh.task_ssh(
        config_key=config_key,
        dir_instance=dir_instance,
        instance_config=yaml_config
    )
    ns.add_task(ssh)

    ssh_port_forward = aws_infrastructure.tasks.library.instance_ssh.task_ssh_port_forward(
        config_key=config_key,
        instance_config=yaml_config
    )
    ns.add_task(ssh_port_forward)

    helm_install = aws_infrastructure.tasks.library.instance_helm.task_helm_install(
        config_key=config_key,
        dir_helm_repo=dir_helm_repo,
        instance_config=yaml_config
    )
    ns.add_task(helm_install)

    helmfile_apply = aws_infrastructure.tasks.library.instance_helmfile.task_helmfile_apply(
        config_key=config_key,
        instance_config=yaml_config
    )
    ns.add_task(helmfile_apply)

    ip = _task_ip(
        config_key=config_key,
        instance_config=yaml_config
    )
    ns.add_task(ip)

    return ns
