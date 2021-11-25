"""
Tasks for configuring the AWS CLI environment.
"""

from dataclasses import dataclass
from invoke import Collection
from invoke import task
from pathlib import Path
from typing import Dict
from typing import List
from typing import Union


@dataclass(frozen=True)
class AWSConfig:
    aws_config_path: Union[Path, str]
    """
    Path to an AWS configuration file.
    """

    profile: str
    """
    Profile within that file.
    """


def _task_configure(*, awsconfig_name: str, awsconfig: AWSConfig):
    @task
    def configure(context):
        """
        Configure AWS CLI for {}.
        """
        # if test.pipenv_pytest_dirs:
        #     for test_dir in test.pipenv_pytest_dirs:
        #         _pipenv_pytest(context=context, test_dir=test_dir)
        pass

    configure.__doc__ = configure.__doc__.format(test_name)

    return configure


def create_tasks(
    *,
    config_key: str,
    awsconfigs: Dict[str, AWSConfig],
):
    ns = Collection('configure')

    for (awsconfig_name_current, awsconfig_current) in awsconfigs.items():
        ns.add_task(
            _task_configure(awsconfig_name=awsconfig_name_current, awsconfig=awsconfig_current),
            name=awsconfig_name_current,
        )

    return ns
