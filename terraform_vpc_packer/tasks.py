from invoke import task
from collections import namedtuple
import os


_terraform_initialized = False
"""Manual de-duplication of initialize."""


@task
def initialize(context):
    """
    Initialize Terraform.

    Pre-tasks do not inherit the context of the task that invokes them,
    so we explicitly pass context and manually de-duplicate initialization.
    """

    global _terraform_initialized
    if _terraform_initialized:
        return

    working_dir = os.path.normpath(context.config.working_dir)
    bin_terraform = os.path.normpath(os.path.join(context.config.bin_dir, 'terraform.exe'))

    with context.cd(working_dir):
        print('Initializing Terraform')
        context.run(
            command='{} {} {}'.format(
                bin_terraform,
                'init',
                '-no-color'
            ),
            hide='stdout'
        )

    _terraform_initialized = True


@task
def create(context):
    """
    Create the VPC used by Packer.
    """

    initialize(context)

    working_dir = os.path.normpath(context.config.working_dir)
    bin_terraform = os.path.normpath(os.path.join(context.config.bin_dir, 'terraform.exe'))

    with context.cd(working_dir):
        print('Creating VPC Packer')
        context.run(
            command='{} {} {}'.format(
                bin_terraform,
                'apply',
                '-auto-approve -no-color'
            ),
        )

        result = context.run(
            command='{} {} {} {}'.format(
                bin_terraform,
                'output',
                '-no-color',
                'vpc_id'
            ),
            hide='stdout'
        )
        vpc_id = result.stdout.strip()

        result = context.run(
            command='{} {} {} {}'.format(
                bin_terraform,
                'output',
                '-no-color',
                'subnet_id'
            ),
            hide='stdout'
        )
        subnet_id = result.stdout.strip()

        return namedtuple('Output', ['vpc_id', 'subnet_id'])(
            vpc_id=vpc_id,
            subnet_id=subnet_id
        )


@task
def destroy(context):
    """
    Destroy the VPC used by Packer.
    """

    initialize(context)

    working_dir = os.path.normpath(context.config.working_dir)
    bin_terraform = os.path.normpath(os.path.join(context.config.bin_dir, 'terraform.exe'))

    with context.cd(working_dir):
        print('Destroying VPC Packer')
        context.run(
            command='{} {} {}'.format(
                bin_terraform,
                'destroy',
                '-auto-approve -no-color'
            ),
        )


class vpc_packer:
    """
    Guard object for creating and destroying the VPC used by Packer.
    """

    vpc_id = None
    subnet_id = None

    def __init__(self, context):
        self._context = context

    def __enter__(self):
        output = create(self._context)
        self.vpc_id = output.vpc_id
        self.subnet_id = output.subnet_id

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        destroy(self._context)
