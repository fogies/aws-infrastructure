from invoke import task


@task
def initialize(context):
    """
    Initialize Terraform.
    """
    with context.cd('terraform_vpc_packer'):
        print('Initializing Terraform')
        context.run(command='..\\bin\\terraform.exe init -no-color')


@task(
    pre=[initialize]
)
def create(context):
    """
    Create the VPC used by Packer.
    """
    with context.cd('terraform_vpc_packer'):
        print('Creating Packer Network')
        context.run(command='..\\bin\\terraform.exe apply -auto-approve -no-color')


@task(
    pre=[initialize]
)
def destroy(context):
    """
    Destroy the VPC used by Packer.
    """
    with context.cd('terraform_vpc_packer'):
        print('Destroying Packer Network')
        context.run(command='..\\bin\\terraform.exe destroy -auto-approve -no-color')


class vpc_packer:
    """
    Guard object for creating and destroying the VPC used by Packer.
    """

    def __init__(self, context):
        self.context = context

    def __enter__(self):
        create(self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        destroy(self.context)
