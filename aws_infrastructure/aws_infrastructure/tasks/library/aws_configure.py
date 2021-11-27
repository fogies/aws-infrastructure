"""
Tasks for configuring the AWS CLI environment.
"""

import configparser
from dataclasses import dataclass
import dotenv
from invoke import Collection
from invoke import task
from pathlib import Path
from typing import Dict
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


def _task_configure(
    *,
    awsenv_path: Path,
    awsconfig: AWSConfig,
    awsconfig_name: str,
):
    @task
    def configure(context):
        """
        Configure AWS CLI for {}.
        """

        config = configparser.SafeConfigParser()
        config.read(awsconfig.aws_config_path)

        config_profile = config['profile {}'.format(awsconfig.profile)]

        with open(awsenv_path, mode='w') as awsenv_file:
            awsenv_file.writelines(['\n'.join([
                '# Generated from:',
                '#   config: {}'.format(awsconfig.aws_config_path),
                '#   profile: {}'.format(awsconfig.profile),
                '',
                '{}={}'.format(
                    'AWS_ACCESS_KEY_ID',
                    config_profile['aws_access_key_id'],
                ),
                '{}={}'.format(
                    'AWS_SECRET_ACCESS_KEY',
                    config_profile['aws_secret_access_key'],
                ),
                '{}={}'.format(
                    'AWS_DEFAULT_REGION',
                    config_profile['region'],
                ),
            ])])

    configure.__doc__ = configure.__doc__.format(awsconfig_name)

    return configure


def create_tasks(
    *,
    config_key: str,
    awsenv_path: Union[Path, str],
    awsconfigs: Dict[str, AWSConfig],
):
    ns = Collection('configure')

    for (awsconfig_name_current, awsconfig_current) in awsconfigs.items():
        ns.add_task(
            _task_configure(
                awsenv_path=awsenv_path,
                awsconfig=awsconfig_current,
                awsconfig_name=awsconfig_name_current,
            ),
            name=awsconfig_name_current,
        )

    return ns


def apply_awsenv(
    *,
    awsenv_path: Union[Path, str],
):
    """
    Apply the environment at the provided path, created by a prior configure task.
    """
    if Path(awsenv_path).exists():
        dotenv.load_dotenv(dotenv_path=awsenv_path, override=True, verbose=True)
