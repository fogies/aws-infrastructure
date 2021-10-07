from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.terraform
from collections import namedtuple
from invoke import Collection
from pathlib import Path
from typing import List
from typing import Union

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

    ns_eip = Collection('eip')

    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        terraform_bin=terraform_bin,
        terraform_dir=terraform_dir,
        output_tuple_factory=namedtuple('eip', ['id', 'public_ip']),
    )

    compose_collection(
        ns_eip,
        ns_terraform,
        sub=False
    )

    return ns_eip


def create_eip_read_only(
    ns_eip: Collection,
):
    """
    Create a read only context manager.
    """

    eip_read_only = aws_infrastructure.tasks.library.terraform.create_context_manager_read_only(
        init=ns_eip.tasks['init'],
        output=ns_eip.tasks['output'],
    )

    return eip_read_only
