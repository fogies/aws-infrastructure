from invoke import task
from terraform_vpc_packer import initialize as vpc_packer_initialize
from terraform_vpc_packer import vpc_packer


@task(
    pre=[vpc_packer_initialize]
)
def build(context):
    """
    Build the AMI Minikube.
    """
    with vpc_packer(context=context) as vpc_packer_output:
        with context.cd('packer_ami_minikube'):
            print('Building AMI Minikube')
            context.run(
                command='{} {} {} {} {} {}'.format(
                    '..\\bin\\packer.exe',
                    'build',
                    '-color=false',
                    '-var "vpc_packer_vpc_id={}"'.format(vpc_packer_output.vpc_id),
                    '-var "vpc_packer_subnet_id={}"'.format(vpc_packer_output.subnet_id),
                    '.'
                )
            )
