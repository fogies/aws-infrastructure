from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.terraform
import base64
import boto3
import botocore
from collections import namedtuple
from invoke import Collection
from pathlib import Path
import re
from typing import List
from typing import Union


def _output_enhance(
    *,
    aws_profile: str,
    aws_shared_credentials_path: Path,
    aws_config_path: Path,
):
    def output_enhance(
        *,
        context,
        output,
    ):
        """
        Enhance the Terraform output with registry authentication information.
        """

        # Obtain an authorization token
        # boto already checked the environment variables, so setting them now has no effect on the default session.
        # Creating a new session prompts boto to check again.
        # We could set/unset the environment variables, but instead configure directly within the boto session.
        boto_session = boto3.Session(botocore_session=botocore.session.Session(
            session_vars={
                'profile': (None, None, aws_profile, None),
                'credentials_file': (None, None, aws_shared_credentials_path, None),
                'config_file': (None, None, aws_config_path, None),
            }
        ))
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

    return output_enhance


def create_tasks(
    *,
    config_key: str,
    terraform_bin: Union[Path, str],
    terraform_dir: Union[Path, str],
    aws_profile: str,
    aws_shared_credentials_path: Union[Path, str],
    aws_config_path: Union[Path, str],
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    terraform_bin = Path(terraform_bin)
    terraform_dir = Path(terraform_dir)
    aws_shared_credentials_path = Path(aws_shared_credentials_path)
    aws_config_path = Path(aws_config_path)

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
        output_enhance=_output_enhance(
            aws_profile=aws_profile,
            aws_shared_credentials_path=aws_shared_credentials_path,
            aws_config_path=aws_config_path,
        ),
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
