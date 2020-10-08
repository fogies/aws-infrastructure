from invoke import task


@task
def create_packer_network(context):
    """
    Create the network used by Packer.
    """
    with context.cd('terraform_packernetwork'):
        print('Creating Packer Network')
        context.run(command='..\\bin\\terraform.exe apply -auto-approve -no-color')


@task
def destroy_packer_network(context):
    """
    Destroy the network used by Packer.
    """
    with context.cd('terraform_packernetwork'):
        print('Destroying Packer Network')
        context.run(command='..\\bin\\terraform.exe destroy -auto-approve -no-color')


class packer_network:
    """
    Guard object for creating and destroying the network used by Packer.
    """

    def __init__(self, context):
        self.context = context

    def __enter__(self):
        create_packer_network(self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        destroy_packer_network(self.context)


@task
def build_ami_minikube(context):
    """
    Build the AMI Minikube.
    """
    with packer_network(context=context):
        with context.cd('ami_minikube'):
            print('Building AMI Minikube')
            context.run(command='..\\bin\\packer.exe build -color=false -var-file=..\\terraform_packernetwork\packernetwork.pkrvars.hcl .', echo=True)
