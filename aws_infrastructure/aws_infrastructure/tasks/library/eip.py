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
    bin_terraform: Union[Path, str],
    dir_terraform: Union[Path, str],
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    bin_terraform = Path(bin_terraform)
    dir_terraform = Path(dir_terraform)

    ns_eip = Collection('eip')

    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        bin_terraform=bin_terraform,
        dir_terraform=dir_terraform,
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
