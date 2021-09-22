from aws_infrastructure.tasks.collection import compose_collection
import aws_infrastructure.tasks.library.terraform
import aws_infrastructure.tasks.library.minikube_instance
from invoke import Collection
from invoke import task
import os
from pathlib import Path
import ruamel.yaml
import shutil
from typing import List
from typing import Union


def _destroy_post_exec(
    *,
    dir_terraform: Path,
    instance_names: List[str],
):
    """
    Create a helper function for the destroy task.
    """

    def delete_empty_instance_dirs(
        *,
        context,
        params,
    ):
        """
        Delete any instance directories which are effectively empty.
        """

        # Terraform will create instance directories to store state files related to SSH.
        # But Terraform will not automatically remove those same instance directories, even if they are empty.
        # Look for these directories, delete them if they are effectively empty.
        for instance_name_current in instance_names:
            # Instance dirs are relative to the Terraform directory
            dir_instance_current = Path(dir_terraform, instance_name_current)
            if dir_instance_current.exists() and dir_instance_current.is_dir():
                # Some children may exist but can be safely deleted.
                # Check if all existing children are known to be safe to delete.
                # If so, delete everything. Otherwise, leave everything.
                safe_to_delete_entries = [
                    'known_hosts',  # Created as part of SSH access
                ]

                # Determine if all existing files are safe to delete
                existing_entries = os.scandir(dir_instance_current)
                unknown_entries = [
                    entry_current
                    for entry_current in existing_entries
                    if entry_current.name not in safe_to_delete_entries
                ]

                # If everything is safe to delete, then go ahead with deletion
                if len(unknown_entries) == 0:
                    shutil.rmtree(dir_instance_current)

    return delete_empty_instance_dirs


def create_tasks(
    *,
    config_key: str,
    bin_terraform: Union[Path, str],
    dir_terraform: Union[Path, str],
    dir_helm_repo: Union[Path, str],
    instance_names: List[str],

    terraform_variables=None,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    bin_terraform = Path(bin_terraform)
    dir_terraform = Path(dir_terraform)
    dir_helm_repo = Path(dir_helm_repo)

    # Collection to compose
    ns = Collection('minikube-helm')

    # Create the terraform tasks
    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        bin_terraform=bin_terraform,
        dir_terraform=dir_terraform,

        terraform_variables=terraform_variables,
        destroy_post_exec=_destroy_post_exec(
            dir_terraform=dir_terraform,
            instance_names=instance_names,
        ),
    )

    # Compose the top-level Terraform tasks
    compose_collection(
        ns,
        ns_terraform,
        sub=False
    )

    # Then create tasks associated with any active instances
    for instance_name_current in instance_names:
        # Instance dirs are relative to the Terraform directory
        dir_instance_current = Path(dir_terraform, instance_name_current)
        path_instance_ssh_config = Path(dir_terraform, instance_name_current, 'ssh_config.yaml')
        if path_instance_ssh_config.exists():
            with open(path_instance_ssh_config) as file_ssh_config:
                yaml_config = ruamel.yaml.safe_load(file_ssh_config)
            ssh_config = aws_infrastructure.tasks.library.instance_ssh.SSHConfig(**yaml_config)

            # Create the instance tasks
            ns_instance = aws_infrastructure.tasks.library.minikube_instance.create_tasks(
                config_key='{}.{}'.format(config_key, instance_name_current),
                dir_terraform=dir_terraform,
                dir_helm_repo=dir_helm_repo,
                instance_name=instance_name_current,
                ssh_config=ssh_config,
            )

            # Compose the instance tasks
            compose_collection(
                ns,
                ns_instance,
                # If there is only 1 instance, its tasks are part of our collection
                # If there are multiple instances, their tasks are each a sub-collection
                sub=len(instance_names) > 1
            )

    return ns
