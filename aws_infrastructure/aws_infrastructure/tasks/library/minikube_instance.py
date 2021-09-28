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
    path_ssh_config: Path
):
    @task
    def ip(context):
        """
        Print the public IP of the instance.
        """
        print(aws_infrastructure.tasks.library.instance_ssh.SSHConfig(path_ssh_config=path_ssh_config).ip)

    return ip


def create_tasks(
    *,
    config_key: str,
    dir_terraform: Union[Path, str],
    dir_helm_repo: Union[Path, str],
    instance_name: str,
    path_ssh_config: Union[Path, str],

    dir_staging_local_helmfile: Union[Path, str],

    dir_staging_remote_helm: Union[Path, str] = None, # '.staging/helm',
    dir_staging_remote_helmfile: Union[Path, str] = None, # '.staging/helmfile'
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    dir_terraform = Path(dir_terraform)
    dir_helm_repo = Path(dir_helm_repo)
    path_ssh_config = Path(path_ssh_config)
    if dir_staging_remote_helm is not None:
        dir_staging_remote_helm = Path(dir_staging_remote_helm)
    if dir_staging_remote_helmfile is not None:
        dir_staging_remote_helmfile = Path(dir_staging_remote_helmfile)

    ns = Collection(instance_name)

    ssh = aws_infrastructure.tasks.library.instance_ssh.task_ssh(
        config_key=config_key,
        path_ssh_config=path_ssh_config,
    )
    ns.add_task(ssh)

    ssh_port_forward = aws_infrastructure.tasks.library.instance_ssh.task_ssh_port_forward(
        config_key=config_key,
        path_ssh_config=path_ssh_config,
    )
    ns.add_task(ssh_port_forward)

    helm_install = aws_infrastructure.tasks.library.instance_helm.task_helm_install(
        config_key=config_key,
        dir_helm_repo=dir_helm_repo,
        path_ssh_config=path_ssh_config,
        dir_staging_remote=dir_staging_remote_helm,
    )
    ns.add_task(helm_install)

    helmfile_apply = aws_infrastructure.tasks.library.instance_helmfile.task_helmfile_apply_generic(
        config_key=config_key,
        path_ssh_config=path_ssh_config,
        dir_staging_local=dir_staging_local_helmfile,
        dir_staging_remote=dir_staging_remote_helmfile,
    )
    ns.add_task(helmfile_apply)

    ip = _task_ip(
        config_key=config_key,
        path_ssh_config=path_ssh_config,
    )
    ns.add_task(ip)

    return ns
