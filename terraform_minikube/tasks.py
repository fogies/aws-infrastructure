from invoke import task


@task
def initialize(context):
    """
    Initialize Terraform.
    """
    with context.cd('terraform_minikube'):
        print('Initializing Terraform')
        context.run(
            command='..\\bin\\terraform.exe init -no-color',
            hide="stdout"
        )


@task(
    pre=[initialize]
)
def create(context):
    """
    Start a Minikube instance.
    """
    with context.cd('terraform_minikube'):
        print('Creating Minikube')
        context.run(command='..\\bin\\terraform.exe apply -auto-approve -no-color')


@task(
    pre=[initialize]
)
def destroy(context):
    """
    Destroy our Minikube instance.
    """
    with context.cd('terraform_minikube'):
        print('Destroying Minikube')
        context.run(command='..\\bin\\terraform.exe destroy -auto-approve -no-color')


@task(
    pre=[initialize]
)
def ssh(context):
    """
    SSH into our Minikube instance.
    """
    print('Creating SSH Session')

    with context.cd('terraform_minikube'):
        result = context.run(
            command='{} output {} {}'.format(
                '..\\bin\\terraform.exe',
                '-no-color',
                'ip'
            ),
            hide="stdout"
        )
        ip = result.stdout.strip()

    with context.cd('terraform_minikube'):
        result = context.run(
            command='{} output {} {}'.format(
                '..\\bin\\terraform.exe',
                '-no-color',
                'identity_file'
            ),
            hide="stdout"
        )
        identity_file = result.stdout.strip()

    with context.cd('terraform_minikube'):
        context.run(
            command='{} {} {} {} {}'.format(
                'start',
                'ssh',
                '-l ubuntu',
                '-i {}'.format(identity_file),
                ip
            ),
            disown=True
        )
