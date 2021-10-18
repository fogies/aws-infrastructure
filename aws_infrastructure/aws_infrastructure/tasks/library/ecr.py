from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.terraform
import base64
import boto3
from collections import namedtuple
from invoke import Collection
from pathlib import Path
import re
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

    # Obtain an authorization token
    boto_ecr = boto3.client('ecr')
    token = boto_ecr.get_authorization_token()['authorizationData'][0]['authorizationToken']

    # Token is base64 encoded, contents are 'user:password'
    token_decoded = base64.standard_b64decode(token).decode('UTF-8')
    match = re.match('(.+):(.+)', token_decoded)
    token_user = match.group(1)
    token_password = match.group(2)

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
        registry_user=token_user,
        registry_password=token_password,
        repository_urls=output.repository_urls,
    )

    return output


def create_tasks(
    *,
    config_key: str,
    terraform_bin: Union[Path, str],
    terraform_dir: Union[Path, str],
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    terraform_bin = Path(terraform_bin)
    terraform_dir = Path(terraform_dir)

    ns_ecr = Collection('ecr')

    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        terraform_bin=terraform_bin,
        terraform_dir=terraform_dir,
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
