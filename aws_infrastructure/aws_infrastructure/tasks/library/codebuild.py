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


def _apply_pre_exec(
    *,
    terraform_dir: Path,
    instances: List[str],
    codebuild_environment_variables_factory, # Dictionary from string to function that returns dictionary
):
    def apply_pre_exec(
        *,
        context,
        params,
    ):
        """
        Prepare CodeBuild archives that Terraform can upload.
        """

        # Create an archive of each source that Terraform can upload to S3
        for instance_current in instances:
            path_source = Path(terraform_dir, instance_current)
            path_staging = Path(terraform_dir, 'staging', instance_current)

            # Copy source into a staging directory
            shutil.rmtree(path=path_staging, ignore_errors=True)
            shutil.copytree(src=path_source, dst=path_staging)

            # Determine whether we need to update the buildspec.yml with environment variables
            if codebuild_environment_variables_factory != None and instance_current in codebuild_environment_variables_factory:
                # Obtain the variables we need to update in the buildspec.yml
                codebuild_environment_variables_current = codebuild_environment_variables_factory[instance_current](context=context)

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
                for key_current, value_current in codebuild_environment_variables_current.items():
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

    return apply_pre_exec


def _destroy_post_exec(
    *,
    terraform_dir: Path,
    instances: List[str],
):
    def destroy_post_exec(
        *,
        context,
        params,
    ):
        """
        Remove CodeBuild archives.
        """

        # Clean up the archives
        for instance_current in instances:
            os.remove(Path(terraform_dir, 'staging', instance_current + '.zip'))

    return destroy_post_exec


def create_tasks(
    *,
    config_key: str,
    terraform_bin: Union[Path, str],
    terraform_dir: Union[Path, str],
    instances: List[str],
    codebuild_environment_variables_factory,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    terraform_bin = Path(terraform_bin)
    terraform_dir = Path(terraform_dir)

    ns_codebuild = Collection('codebuild')

    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        terraform_bin=terraform_bin,
        terraform_dir=terraform_dir,
        apply_pre_exec=_apply_pre_exec(
            terraform_dir=terraform_dir,
            instances=instances,
            codebuild_environment_variables_factory=codebuild_environment_variables_factory,
        ),
        destroy_post_exec=_destroy_post_exec(
            terraform_dir=terraform_dir,
            instances=instances
        ),
    )

    compose_collection(
        ns_codebuild,
        ns_terraform,
        sub=False,
    )

    # Create tasks associated with our instances
    for instance_current in instances:
        ns_instance = aws_infrastructure.tasks.library.codebuild_instance.create_tasks(
            config_key='{}.{}'.format(config_key, instance_current),
            task_apply=ns_codebuild.tasks['apply'],
            instance=instance_current,
        )

        compose_collection(ns_codebuild, ns_instance)

    return ns_codebuild
