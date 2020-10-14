from invoke import task
from terraform_vpc_packer import vpc_packer


@task
def build(context):
    """
    Build the AMI Minikube.
    """
    with vpc_packer(context=context):
        with context.cd('packer_ami_minikube'):
            print('Building AMI Minikube')
            context.run(
                command='{} build {} -var-file={} .'.format(
                    '..\\bin\\packer.exe',
                    '-color=false',
                    '..\\terraform_vpc_packer\\vpc_packer.pkrvars.hcl'
                )
            )
