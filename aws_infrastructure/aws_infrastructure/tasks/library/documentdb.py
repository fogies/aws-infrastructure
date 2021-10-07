from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.terraform
from collections import namedtuple
from invoke import Collection
from pathlib import Path
from typing import Union

def create_tasks(
    *,
    config_key: str,
    bin_terraform: Union[Path, str],
    dir_terraform: Union[Path, str],

    terraform_variables_factory=None,
    terraform_variables_path: Union[Path, str] = None,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    bin_terraform = Path(bin_terraform)
    dir_terraform = Path(dir_terraform)
    terraform_variables_path = Path(terraform_variables_path) if terraform_variables_path else None

    ns_documentdb = Collection('documentdb')

    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        bin_terraform=bin_terraform,
        dir_terraform=dir_terraform,
        output_tuple_factory=namedtuple(
            'documentdb',
            [
                'admin_user',
                'admin_password',
                'endpoint',
                'hosts',
            ]
        ),

        terraform_variables_factory=terraform_variables_factory,
        terraform_variables_path=terraform_variables_path,
    )

    compose_collection(
        ns_documentdb,
        ns_terraform,
        sub=False
    )

    return ns_documentdb
