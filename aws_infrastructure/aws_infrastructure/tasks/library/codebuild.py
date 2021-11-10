from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.terraform
import boto3
from collections import namedtuple
from invoke import Collection
from invoke import task
import os
import os.path
from pathlib import Path
import ruamel.yaml
import shutil
import time
from typing import List
from typing import Union


def _task_create_build_archive(
    *,
    config_key: str,
    terraform_dir: Path,
    staging_local_dir: Path,
    staging_local_source_dir: Path,
    staging_local_archive_path: Path,
    source_dir: Path,
    codebuild_environment_variables_factory, # Function that returns dictionary
):
    @task
    def create_build_archive(context):
        """
        Prepare the CodeBuild archive for Terraform to upload.
        """

        # Remove any prior staging
        shutil.rmtree(path=staging_local_dir, ignore_errors=True)

        # Copy source into a staging directory
        shutil.copytree(src=source_dir, dst=staging_local_source_dir)

        # Determine whether we need to update the buildspec.yml with environment variables
        if codebuild_environment_variables_factory != None:
            # Obtain the variables we need to update in the buildspec.yml
            codebuild_environment_variables = codebuild_environment_variables_factory(context=context)

            # Use a parsing object for roundtrip
            # Invoking a parse without keeping the object will not maintain state for round trip
            yaml_parser = ruamel.yaml.YAML()
            buildspec_path = Path(staging_local_source_dir, 'buildspec.yml')

            # Update the buildspec to add provided environment variables
            with open(buildspec_path) as file_buildspec:
                yaml_buildspec = yaml_parser.load(file_buildspec)

            # Ensure the buildspec provides for environment variables
            if 'env' not in yaml_buildspec:
                yaml_buildspec['env'] = {}
            if 'variables' not in yaml_buildspec['env']:
                yaml_buildspec['env']['variables'] = {}

            # Add the variables
            for key_current, value_current in codebuild_environment_variables.items():
                yaml_buildspec['env']['variables'][key_current] = value_current

            # Replace the buildspec
            os.remove(buildspec_path)
            with open(buildspec_path, mode='w') as file_buildspec:
                yaml_parser.dump(yaml_buildspec, file_buildspec)

        # Make the archive
        shutil.make_archive(
            # Remove the zip suffix because make_archive will also apply that suffix
            base_name=Path(staging_local_archive_path.parent, staging_local_archive_path.stem),
            format='zip',
            root_dir=staging_local_source_dir
        )

    return create_build_archive


def _task_execute_build(
    *,
    config_key: str,
    codebuild_project_name: str,
):
    @task
    def execute_build(context):
        """
        Execute the build and print any output.
        """

        boto_cloudwatchlogs = boto3.client('logs')
        boto_codebuild = boto3.client('codebuild')

        # Start the build
        response = boto_codebuild.start_build(projectName=codebuild_project_name)
        build_id = response['build']['id']

        # Loop on the build until logs become available
        in_progress = True
        logs_next_token = None
        while in_progress:
            # Determine whether the build is still executing
            response_build = boto_codebuild.batch_get_builds(ids=[build_id])['builds'][0]
            in_progress = response_build['buildStatus'] == 'IN_PROGRESS'

            # If the logs have been created
            events_available = False
            if 'groupName' in response_build['logs'] and 'streamName' in response_build['logs']:
                # Print any logs that are currently available
                events_available = True
                while events_available:
                    if logs_next_token is None:
                        response_logs = boto_cloudwatchlogs.get_log_events(
                            logGroupName=response_build['logs']['groupName'],
                            logStreamName=response_build['logs']['streamName'],
                            startFromHead=True
                        )
                    else:
                        response_logs = boto_cloudwatchlogs.get_log_events(
                            logGroupName=response_build['logs']['groupName'],
                            logStreamName=response_build['logs']['streamName'],
                            nextToken=logs_next_token,
                            startFromHead=True
                        )

                    for event_current in response_logs['events']:
                        print(event_current['message'], end='', flush=True)

                    events_available = response_logs['nextForwardToken'] != logs_next_token
                    logs_next_token = response_logs['nextForwardToken']

            if in_progress:
                # Any faster will likely encounter rate limiting
                time.sleep(.5)

    return execute_build


def create_tasks(
    *,
    config_key: str,
    terraform_bin: Union[Path, str],
    terraform_dir: Union[Path, str],
    staging_local_dir: Union[Path, str],
    source_dir: Union[Path, str],
    codebuild_project_name: str,
    codebuild_environment_variables_factory,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    terraform_bin = Path(terraform_bin)
    terraform_dir = Path(terraform_dir)
    staging_local_dir = Path(staging_local_dir)
    source_dir = Path(source_dir)

    staging_local_source_dir = Path(staging_local_dir, 'source')
    staging_local_archive_path = Path(staging_local_dir, 'archive.zip')
    terraform_variables_path = Path(terraform_dir, 'variables.generated.tfvars')

    def terraform_variables_factory(*, context):
        return {
            'source_archive': os.path.relpath(staging_local_archive_path,terraform_dir)
        }

    ns_codebuild = Collection('codebuild')

    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        terraform_bin=terraform_bin,
        terraform_dir=terraform_dir,
        terraform_variables_factory=terraform_variables_factory,
        terraform_variables_path=terraform_variables_path,
    )

    create_build_archive = _task_create_build_archive(
        config_key=config_key,
        terraform_dir=terraform_dir,
        staging_local_dir=staging_local_dir,
        staging_local_source_dir=staging_local_source_dir,
        staging_local_archive_path=staging_local_archive_path,
        source_dir=source_dir,
        codebuild_environment_variables_factory=codebuild_environment_variables_factory,
    )

    execute_build = _task_execute_build(
        config_key=config_key,
        codebuild_project_name=codebuild_project_name,
    )


    @task(pre=[create_build_archive, ns_terraform.tasks['apply'], execute_build])
    def build(context):
        """
        Build the Docker image.

        The actual build happens in the sequence of pre-requisite tasks
        """
        pass


    ns_codebuild.add_task(build, name="build")
    compose_collection(
        ns_codebuild,
        ns_terraform,
        sub=False,
        include=[
            'destroy',
        ],
    )

    return ns_codebuild
