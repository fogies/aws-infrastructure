from invoke import task
from collections import namedtuple


@task
def initialize(context):
    """
    Initialize Terraform.
    """
    with context.cd('terraform_vpc_packer'):
        print('Initializing Terraform')
        context.run(
            command='{} {} {}'.format(
                '..\\bin\\terraform.exe',
                'init',
                '-no-color'
            ),
            hide='stdout'
        )


@task(
    pre=[initialize]
)
def create(context):
    """
    Create the VPC used by Packer.
    """
    with context.cd('terraform_vpc_packer'):
        print('Creating VPC Packer')
        context.run(
            command='{} {} {}'.format(
                '..\\bin\\terraform.exe',
                'apply',
                '-auto-approve -no-color'
            ),
        )

        result = context.run(
            command='{} {} {} {}'.format(
                '..\\bin\\terraform.exe',
                'output',
                '-no-color',
                'vpc_id'
            ),
            hide='stdout'
        )
        vpc_id = result.stdout.strip()

        result = context.run(
            command='{} {} {} {}'.format(
                '..\\bin\\terraform.exe',
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


@task(
    pre=[initialize]
)
def destroy(context):
    """
    Destroy the VPC used by Packer.
    """
    with context.cd('terraform_vpc_packer'):
        print('Destroying VPC Packer')
        context.run(
            command='{} {} {}'.format(
                '..\\bin\\terraform.exe',
                'destroy',
                '-auto-approve -no-color'
            ),
        )


class vpc_packer:
    """
    Guard object for creating and destroying the VPC used by Packer.

    Tasks that use this will also need a pre-task for initialize.
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
