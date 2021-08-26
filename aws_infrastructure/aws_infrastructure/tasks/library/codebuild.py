from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.codebuild_instance
import aws_infrastructure.tasks.library.terraform
from collections import namedtuple
from invoke import Collection
from invoke import task
import os
from pathlib import Path
import ruamel.yaml
import shutil
from typing import List
from typing import Union


def create_tasks(
    *,
    config_key: str,
    bin_terraform: Union[Path, str],
    dir_terraform: Union[Path, str],
    instances: List[str],
    environment_variables
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
            path_source = Path(dir_terraform, instance_current)
            path_staging = Path(dir_terraform, 'staging', instance_current)

            # Copy source into a staging directory
            shutil.rmtree(path=path_staging, ignore_errors=True)
            shutil.copytree(src=path_source, dst=path_staging)

            # Determine whether we need to update the buildspec.yml with environment variables
            if environment_variables != None and instance_current in environment_variables:
                # Obtain the variables we need to update in the buildspec.yml
                environment_variables_current = environment_variables[instance_current](context=context)

                # Use a parsing object for roundtrip
                yaml_parser = ruamel.yaml.YAML()
                path_buildspec = Path(path_staging, 'buildspec.yml')

                # Update the buildspec to add provided environment variables
                with open(path_buildspec) as file_buildspec:
                    yaml_buildspec = yaml_parser.load(file_buildspec)

                # Ensure the buildspec provides for environment variables
                if 'env' not in yaml_buildspec:
                    yaml_buildspec['env'] = {}
                if 'variables' not in yaml_buildspec['env']:
                    yaml_buildspec['env']['variables'] = {}

                # Add the variables
                for key_current, value_current in environment_variables_current.items():
                    yaml_buildspec['env']['variables'][key_current] = value_current

                # Replace the buildspec
                os.remove(path_buildspec)
                with open(path_buildspec, mode='w') as file_buildspec:
                    yaml_parser.dump(yaml_buildspec, file_buildspec)

            # Make the archive
            shutil.make_archive(
                base_name=path_staging,
                format='zip',
                root_dir=path_staging
            )

            # Remove the staged source directory
            shutil.rmtree(
                path=path_staging,
                ignore_errors=True
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
