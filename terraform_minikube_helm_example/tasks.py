from invoke import task
import os
import shutil


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
    list_instance_dir = ['instance_1', 'instance_2']
    for instance_dir_current in list_instance_dir:
        if os.path.isdir(os.path.normpath(os.path.join(working_dir, instance_dir_current))):
            shutil.rmtree(os.path.normpath(os.path.join(working_dir, instance_dir_current)))
