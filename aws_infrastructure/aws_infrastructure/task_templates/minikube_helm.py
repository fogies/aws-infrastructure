import os
import shutil
from typing import List

import aws_infrastructure.task_templates.terraform
import aws_infrastructure.task_templates.minikube_helm_instance
from invoke import Collection
from invoke import task


# Define and import tasks
def task_delete_empty_instance_dirs(
    *,
    config_key: str
):
    """
    Create a task to delete any instance directories which are effectively empty.
    """

    @task
    def delete_empty_instance_dirs(context):
        """
        Delete any instance directories which are effectively empty.
        """

        config = context.config[config_key]
        working_dir = os.path.normpath(config.working_dir)
        instance_dirs = config.instance_dirs

        # Terraform will create instance directories to store state files related to SSH.
        # But Terraform will not automatically remove those same instance directories, even if they are empty.
        # Look for these directories, delete them if they are effectively empty.
        for instance_dir_current in instance_dirs:
            instance_dir_path = os.path.normpath(os.path.join(working_dir, instance_dir_current))
            if os.path.exists(instance_dir_path) and os.path.isdir(instance_dir_path):
                # Some children may exist but can be safely deleted.
                # Check if all existing children are known to be safe to delete.
                # If so, delete everything. Otherwise, leave everything.
                safe_to_delete_entries = [
                    'known_hosts',  # Created as part of SSH access
                ]

                # Determine if all existing files are safe to delete
                existing_entries = os.scandir(instance_dir_path)
                unknown_entries = [
                    entry_current
                    for entry_current in existing_entries
                    if entry_current.name not in safe_to_delete_entries
                ]

                # If everything is safe to delete, then go ahead with deletion
                if len(unknown_entries) == 0:
                    shutil.rmtree(instance_dir_path)

    return delete_empty_instance_dirs


def create_tasks(
    *,
    config_key: str,
    working_dir: str,
    instance_dirs: List[str],

    variables=None,
    apply_pre: List[task] = None,
    apply_post: List[task] = None,
    destroy_pre: List[task] = None,
    destroy_post: List[task] = None,
    output_tuple_factory=None,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    ns = Collection('minikube_helm')

    # First create the top-level Terraform-related tasks

    delete_empty_instance_dirs = task_delete_empty_instance_dirs(
        config_key=config_key
    )
    combined_destroy_post = [delete_empty_instance_dirs]
    combined_destroy_post.extend(destroy_post or [])

    terraform_tasks = aws_infrastructure.task_templates.terraform.create_tasks(
        config_key=config_key,
        variables=variables,
        apply_pre=apply_pre,
        apply_post=apply_post,
        destroy_pre=destroy_pre,
        destroy_post=combined_destroy_post,
        output_tuple_factory=output_tuple_factory
    )

    for task_current in terraform_tasks.tasks.values():
        ns.add_task(task_current)

    # Then create tasks associated with any active instances
    for instance_dir_current in instance_dirs:
        instance_dir_path = os.path.normpath(os.path.join(working_dir, instance_dir_current))
        if os.path.isdir(instance_dir_path):
            ns.add_collection(aws_infrastructure.task_templates.minikube_helm_instance.create_tasks(
                config_key=config_key,
                working_dir=working_dir,
                instance_dir=instance_dir_current
            ))

    return ns
