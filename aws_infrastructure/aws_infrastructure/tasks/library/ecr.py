from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.terraform
import boto3
from collections import namedtuple
from invoke import Collection
from pathlib import Path
from typing import List
from typing import Union


def _output_enhance(
    *,
    context,
    output,
):
    """
    Enhance the Terraform output with registry authentication information.
    """

    boto_ecr = boto3.client('ecr')

    output = namedtuple(
        'ecr',
        [
            'registry_url',
            'registry_user',
            'registry_password',
            'repository_urls',
        ]
    )(
        registry_url=output.registry_url,
        registry_user='AWS',
        registry_password=boto_ecr.get_authorization_token()['authorizationData'][0]['authorizationToken'],
        repository_urls=output.repository_urls,
    )

    return output


def create_tasks(
    *,
    config_key: str,
    bin_terraform: Union[Path, str],
    dir_terraform: Union[Path, str],
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    bin_terraform = Path(bin_terraform)
    dir_terraform = Path(dir_terraform)

    ns_ecr = Collection('ecr')

    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        bin_terraform=bin_terraform,
        dir_terraform=dir_terraform,
        output_tuple_factory=namedtuple(
            'ecr',
            [
                'registry_url',
                'repository_urls'
            ]
        ),
        output_enhance=_output_enhance,
    )

    compose_collection(
        ns_ecr,
        ns_terraform,
        sub=False
    )

    return ns_ecr


def create_ecr_read_only(
    ns_ecr: Collection,
):
    """
    Create a read only context manager.
    """

    ecr_read_only = aws_infrastructure.tasks.library.terraform.create_context_manager_read_only(
        init=ns_ecr.tasks['init'],
        output=ns_ecr.tasks['output'],
    )

    return ecr_read_only
