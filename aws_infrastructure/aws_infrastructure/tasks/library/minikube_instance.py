from invoke import Collection
from invoke import task
from pathlib import Path
from typing import Union

import aws_infrastructure.tasks.library.instance_helm
import aws_infrastructure.tasks.library.instance_helmfile
import aws_infrastructure.tasks.library.instance_ssh


def _task_ip(
    *,
    config_key: str,
    ssh_config: aws_infrastructure.tasks.library.instance_ssh.SSHConfig
):
    @task
    def ip(context):
        """
        Print the public IP of the instance.
        """
        print(ssh_config.ip)

    return ip


def create_tasks(
    *,
    config_key: str,
    dir_terraform: Union[Path, str],
    dir_helm_repo: Union[Path, str],
    instance_name: str,
    ssh_config: aws_infrastructure.tasks.library.instance_ssh.SSHConfig,

    dir_staging_local_helmfile: Union[Path, str],

    dir_staging_remote_helm: Union[Path, str] = '.staging/helm',
    dir_staging_remote_helmfile: Union[Path, str] = '.staging/helmfile',
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    dir_terraform = Path(dir_terraform)
    dir_instance = Path(dir_terraform, instance_name)
    dir_helm_repo = Path(dir_helm_repo)
    dir_staging_remote_helm = Path(dir_staging_remote_helm)
    dir_staging_remote_helmfile = Path(dir_staging_remote_helmfile)

    ns = Collection(instance_name)

    ssh = aws_infrastructure.tasks.library.instance_ssh.task_ssh(
        config_key=config_key,
        dir_instance=dir_instance,
        ssh_config=ssh_config,
    )
    ns.add_task(ssh)

    ssh_port_forward = aws_infrastructure.tasks.library.instance_ssh.task_ssh_port_forward(
        config_key=config_key,
        ssh_config=ssh_config,
    )
    ns.add_task(ssh_port_forward)

    helm_install = aws_infrastructure.tasks.library.instance_helm.task_helm_install(
        config_key=config_key,
        dir_helm_repo=dir_helm_repo,
        ssh_config=ssh_config,
        dir_staging_remote=dir_staging_remote_helm,
    )
    ns.add_task(helm_install)

    helmfile_apply = aws_infrastructure.tasks.library.instance_helmfile.task_helmfile_apply(
        config_key=config_key,
        ssh_config=ssh_config,
        dir_staging_local=dir_staging_local_helmfile,
        dir_staging_remote=dir_staging_remote_helmfile,
    )
    ns.add_task(helmfile_apply)

    ip = _task_ip(
        config_key=config_key,
        ssh_config=ssh_config,
    )
    ns.add_task(ip)

    return ns
