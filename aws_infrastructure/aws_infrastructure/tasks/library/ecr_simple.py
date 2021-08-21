from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.terraform
from collections import namedtuple
from invoke import Collection


def create_tasks(
    *,
    config_key: str,
    bin_terraform: str,
    dir_terraform: str,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    ns_ecr = Collection('ecr')

    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        bin_terraform=bin_terraform,
        dir_terraform=dir_terraform,
        output_tuple_factory=namedtuple('ecr', ['repository_url']),
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
