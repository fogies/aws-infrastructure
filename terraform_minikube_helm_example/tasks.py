from invoke import task
import os


@task
def initialize(context):
    """
    Initialize Terraform.
    """

    config = context.config.terraform_minikube_helm_example
    working_dir = os.path.normpath(config.working_dir)
    bin_terraform = os.path.normpath(os.path.join(config.bin_dir, 'terraform.exe'))

    with context.cd(working_dir):
        print('Initializing Terraform')
        context.run(
            command='{} {} {}'.format(
                bin_terraform,
                'init',
                '-no-color'
            ),
            hide="stdout"
        )


@task(
    pre=[initialize]
)
def create(context):
    """
    Start a Minikube instance.
    """

    config = context.config.terraform_minikube_helm_example
    working_dir = os.path.normpath(config.working_dir)
    bin_terraform = os.path.normpath(os.path.join(config.bin_dir, 'terraform.exe'))

    with context.cd(working_dir):
        print('Creating Minikube')
        context.run(
            command='{} {} {}'.format(
                bin_terraform,
                'apply',
                '-auto-approve -no-color'
            )
        )


@task(
    pre=[initialize]
)
def destroy(context):
    """
    Destroy our Minikube instance.
    """

    config = context.config.terraform_minikube_helm_example
    working_dir = os.path.normpath(config.working_dir)
    bin_terraform = os.path.normpath(os.path.join(config.bin_dir, 'terraform.exe'))

    with context.cd(working_dir):
        print('Destroying Minikube')
        context.run(
            command='{} {} {}'.format(
                bin_terraform,
                'destroy',
                '-auto-approve -no-color'
            )
        )

        # Terraform will create but not automatically remove instance directories
        if os.path.isdir('terraform_minikube_helm_example/instance_1'):
            os.rmdir('terraform_minikube_helm_example/instance_1')
        if os.path.isdir('terraform_minikube_helm_example/instance_2'):
            os.rmdir('terraform_minikube_helm_example/instance_2')
