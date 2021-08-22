from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.minikube_helm
from invoke import Collection

CONFIG_KEY = 'examples_minikube_helm'
BIN_TERRAFORM = './bin/terraform.exe'
DIR_TERRAFORM = './examples/minikube_helm'
DIR_HELM_REPO = './helm_repo'
DIR_INSTANCES = ['instance']

ns = Collection('minikube-helm')

ns_minikube_helm = aws_infrastructure.tasks.library.minikube_helm.create_tasks(
    config_key=CONFIG_KEY,
    bin_terraform=BIN_TERRAFORM,
    dir_terraform=DIR_TERRAFORM,
    dir_helm_repo=DIR_HELM_REPO,
    dir_instances=DIR_INSTANCES,
)

compose_collection(
    ns,
    ns_minikube_helm,
    sub=False,
    exclude=[
        'init'
    ]
)
