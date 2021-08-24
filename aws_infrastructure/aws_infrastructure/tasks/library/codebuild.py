from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.codebuild_instance
import aws_infrastructure.tasks.library.terraform
from collections import namedtuple
from invoke import Collection
from invoke import task
import os
from pathlib import Path
import shutil
from typing import List
from typing import Union


def create_tasks(
    *,
    config_key: str,
    bin_terraform: Union[Path, str],
    dir_terraform: Union[Path, str],
    instances: List[str],
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    # Collection to compose
    ns_codebuild = Collection('codebuild')

    # Create the terraform tasks
    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        bin_terraform=bin_terraform,
        dir_terraform=dir_terraform,
    )

    # Enhance the apply task
    @task
    def apply(context):
        """
        Issue a Terraform apply.
        """

        # Create an archive of each source that Terraform can upload to S3
        for instance_current in instances:
            shutil.make_archive(
                base_name=str(Path(dir_terraform, 'staging', instance_current)),
                format='zip',
                root_dir=Path(dir_terraform, instance_current)
            )

        # Execute the underlying task
        ns_terraform['apply'](context)

    # Enhance the destroy task
    @task
    def destroy(context):
        """
        Issue a Terraform destroy.
        """

        # Clean up the archives
        for instance_current in instances:
            os.remove(Path(dir_terraform, 'staging', instance_current + '.zip'))

        # Execute the underlying task
        ns_terraform['destroy'](context)

    # Compose the enhanced tasks
    compose_collection(
        ns_codebuild,
        ns_terraform,
        sub=False,
    )

    ns_codebuild.add_task(apply)
    ns_codebuild.add_task(destroy)

    # Create tasks associated with our instances
    for instance_current in instances:
        ns_instance = aws_infrastructure.tasks.library.codebuild_instance.create_tasks(
            config_key='{}.{}'.format(config_key, instance_current),
            task_apply=ns_codebuild.tasks['apply'],
            instance=instance_current,
        )

        compose_collection(ns_codebuild, ns_instance)

    return ns_codebuild
