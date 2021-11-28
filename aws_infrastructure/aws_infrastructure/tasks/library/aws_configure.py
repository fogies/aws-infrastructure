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
    aws_env_path: Path,
    aws_config: AWSConfig,
    aws_config_name: str,
):
    @task
    def configure(context):
        """
        Configure AWS CLI for {}.
        """

        config = configparser.SafeConfigParser()
        config.read(aws_config.aws_config_path)

        config_profile = config['profile {}'.format(aws_config.profile)]

        with open(aws_env_path, mode='w') as awsenv_file:
            awsenv_file.writelines(['\n'.join([
                '# Generated from:',
                '#   config: {}'.format(aws_config.aws_config_path),
                '#   profile: {}'.format(aws_config.profile),
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

    configure.__doc__ = configure.__doc__.format(aws_config_name)

    return configure


def create_tasks(
    *,
    config_key: str,
    aws_env_path: Union[Path, str],
    aws_configs: Dict[str, AWSConfig],
):
    ns = Collection('configure')

    for (aws_config_name, aws_config_current) in aws_configs.items():
        ns.add_task(
            _task_configure(
                aws_env_path=aws_env_path,
                aws_config=aws_config_current,
                aws_config_name=aws_config_name,
            ),
            name=aws_config_name,
        )

    return ns


def apply_aws_env(
    *,
    aws_env_path: Union[Path, str],
):
    """
    Apply the environment at the provided path, created by a prior configure task.
    """
    if Path(aws_env_path).exists():
        dotenv.load_dotenv(dotenv_path=aws_env_path, override=True, verbose=True)
