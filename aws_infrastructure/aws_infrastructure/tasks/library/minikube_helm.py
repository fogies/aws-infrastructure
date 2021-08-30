from aws_infrastructure.tasks.collection import compose_collection
import aws_infrastructure.tasks.library.terraform
import aws_infrastructure.tasks.library.minikube_helm_instance
from invoke import Collection
from invoke import task
import os
from pathlib import Path
import shutil
from typing import List
from typing import Union


# Define and import tasks
def _task_delete_empty_instance_dirs(
    *,
    config_key: str,
    dir_terraform: Path,
    instances: List[str],
):
    """
    Create a task to delete any instance directories which are effectively empty.
    """

    @task
    def delete_empty_instance_dirs(context):
        """
        Delete any instance directories which are effectively empty.
        """

        # Terraform will create instance directories to store state files related to SSH.
        # But Terraform will not automatically remove those same instance directories, even if they are empty.
        # Look for these directories, delete them if they are effectively empty.
        for instance_current in instances:
            # Instance dirs are relative to the Terraform directory
            dir_instance_current = Path(dir_terraform, instance_current)
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
    instances: List[str],
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    bin_terraform = Path(bin_terraform)
    dir_terraform = Path(dir_terraform)
    dir_helm_repo = Path(dir_helm_repo)

    # Collection to compose
    ns = Collection('minikube-helm')

    # Create a post-processing task for deleting empty instance dirs
    delete_empty_instance_dirs = _task_delete_empty_instance_dirs(
        config_key=config_key,
        dir_terraform=dir_terraform,
        instances=instances
    )
    destroy_post = [delete_empty_instance_dirs]

    # Create the terraform tasks
    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        bin_terraform=bin_terraform,
        dir_terraform=dir_terraform,

        destroy_post=destroy_post,
    )

    # Compose the top-level Terraform tasks
    compose_collection(
        ns,
        ns_terraform,
        sub=False
    )

    # Then create tasks associated with any active instances
    for instance_current in instances:
        # Instance dirs are relative to the Terraform directory
        dir_instance_current = Path(dir_terraform, instance_current)
        path_instance_config = Path(dir_terraform, instance_current, 'config.yaml')
        if path_instance_config.exists():
            # Create the instance tasks
            ns_instance = aws_infrastructure.tasks.library.minikube_helm_instance.create_tasks(
                config_key='{}.{}'.format(config_key, instance_current),
                dir_terraform=dir_terraform,
                dir_helm_repo=dir_helm_repo,
                instance=instance_current
            )

            # Compose the instance tasks
            compose_collection(ns, ns_instance)

    return ns
