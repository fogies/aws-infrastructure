from invoke import Collection
from invoke import task
from pathlib import Path
from typing import Union

import aws_infrastructure.tasks.library.instance_helm
import aws_infrastructure.tasks.library.instance_helmfile
import aws_infrastructure.tasks.library.instance_ssh
import aws_infrastructure.tasks.ssh


def _task_ip(
    *,
    config_key: str,
    ssh_config_path: Path
):
    @task
    def ip(context):
        """
        Public IP of the instance.
        """
        print(aws_infrastructure.tasks.ssh.SSHConfig.load(ssh_config_path=ssh_config_path).ip)

    return ip


def create_tasks(
    *,
    config_key: str,
    terraform_dir: Union[Path, str],
    helm_repo_dir: Union[Path, str],
    instance_name: str,
    ssh_config_path: Union[Path, str],

    staging_local_helmfile_dir: Union[Path, str],
    staging_remote_helm_dir: Union[Path, str],
    staging_remote_helmfile_dir: Union[Path, str],
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    terraform_dir = Path(terraform_dir)
    helm_repo_dir = Path(helm_repo_dir)
    ssh_config_path = Path(ssh_config_path)
    staging_remote_helm_dir = Path(staging_remote_helm_dir)
    staging_remote_helmfile_dir = Path(staging_remote_helmfile_dir)

    ns = Collection(instance_name)

    ssh = aws_infrastructure.tasks.library.instance_ssh.task_ssh(
        config_key=config_key,
        ssh_config_path=ssh_config_path,
    )
    ns.add_task(ssh)

    ssh_port_forward = aws_infrastructure.tasks.library.instance_ssh.task_ssh_port_forward(
        config_key=config_key,
        ssh_config_path=ssh_config_path,
    )
    ns.add_task(ssh_port_forward)

    helm_install = aws_infrastructure.tasks.library.instance_helm.task_helm_install(
        config_key=config_key,
        helm_repo_dir=helm_repo_dir,
        ssh_config_path=ssh_config_path,
        staging_remote_dir=staging_remote_helm_dir,
    )
    ns.add_task(helm_install)

    helmfile_apply = aws_infrastructure.tasks.library.instance_helmfile.task_helmfile_apply_generic(
        config_key=config_key,
        ssh_config_path=ssh_config_path,
        staging_local_dir=staging_local_helmfile_dir,
        staging_remote_dir=staging_remote_helmfile_dir,
    )
    ns.add_task(helmfile_apply)

    ip = _task_ip(
        config_key=config_key,
        ssh_config_path=ssh_config_path,
    )
    ns.add_task(ip)

    return ns
