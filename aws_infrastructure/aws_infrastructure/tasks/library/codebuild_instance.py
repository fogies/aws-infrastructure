from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.codebuild
import boto3
from invoke import Collection
from invoke import task
from pathlib import Path
import shutil
import time
from typing import Union

def _task_build(
    *,
    config_key: str,
    task_apply: task,
    instance: str
):
    # Ensure task parameters are explicit to inform deduplication
    @task(
        pre=[task_apply]
    )
    def build(context, config_key=config_key, instance=instance):
        """
        Start a build.
        """
        boto_cloudwatchlogs = boto3.client('logs')
        boto_codebuild = boto3.client('codebuild')

        # Start the build
        response = boto_codebuild.start_build(
            projectName=instance
        )
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

    return build


def create_tasks(
    *,
    config_key: str,
    task_apply: task,
    instance: str,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    ns = Collection(instance)

    build = _task_build(
        config_key=config_key,
        task_apply=task_apply,
        instance=instance,
    )
    ns.add_task(build)

    return ns
