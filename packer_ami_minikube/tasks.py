from invoke import task
import terraform_vpc_packer
import os


@task(pre=[terraform_vpc_packer.initialize])
def build(context):
    """
    Build the AMI Minikube.
    """

    config = context.config.packer_ami_minikube
    working_dir = os.path.normpath(config.working_dir)
    bin_packer = os.path.normpath(os.path.join(config.bin_dir, 'packer.exe'))

    with terraform_vpc_packer.vpc_packer(context=context) as vpc_packer_output:
        with context.cd(working_dir):
            print('Building AMI Minikube')
            context.run(
                command='{} {} {} {} {} {}'.format(
                    bin_packer,
                    'build',
                    '-color=false',
                    '-var "vpc_packer_vpc_id={}"'.format(vpc_packer_output.vpc_id),
                    '-var "vpc_packer_subnet_id={}"'.format(vpc_packer_output.subnet_id),
                    '.'
                )
            )
