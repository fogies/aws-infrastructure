from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.minikube
import aws_infrastructure.tasks.library.terraform
from invoke import Collection

CONFIG_KEY = 'examples_minikube_multiple'
BIN_TERRAFORM = './bin/terraform.exe'
DIR_TERRAFORM = './examples/minikube_multiple'
DIR_HELM_REPO = './helm_repo'
INSTANCE_NAMES = ['amd64_medium', 'amd64_large']

ns = Collection('minikube-multiple')

ns_minikube = aws_infrastructure.tasks.library.minikube.create_tasks(
    config_key=CONFIG_KEY,
    bin_terraform=BIN_TERRAFORM,
    dir_terraform=DIR_TERRAFORM,
    dir_helm_repo=DIR_HELM_REPO,
    instance_names=INSTANCE_NAMES,
)

compose_collection(
    ns,
    ns_minikube,
    sub=False,
    exclude=aws_infrastructure.tasks.library.terraform.exclude_destroy_without_state(
        dir_terraform=DIR_TERRAFORM,
        exclude=[
            'init',
        ],
    )
)
