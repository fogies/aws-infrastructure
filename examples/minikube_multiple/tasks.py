from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.minikube
import aws_infrastructure.tasks.library.terraform
from invoke import Collection

CONFIG_KEY = 'examples_minikube_multiple'
TERRAFORM_BIN = './bin/terraform.exe'
TERRAFORM_DIR = './examples/minikube_multiple'
HELM_REPO_DIR = './helm_repo'
STAGING_LOCAL_HELMFILE_DIR = './.staging/helmfile'
INSTANCE_NAMES = ['amd64_medium', 'amd64_large']

ns = Collection('minikube-multiple')

ns_minikube = aws_infrastructure.tasks.library.minikube.create_tasks(
    config_key=CONFIG_KEY,
    terraform_bin=TERRAFORM_BIN,
    terraform_dir=TERRAFORM_DIR,
    helm_repo_dir=HELM_REPO_DIR,
    staging_local_helmfile_dir=STAGING_LOCAL_HELMFILE_DIR,
    instance_names=INSTANCE_NAMES,
)

compose_collection(
    ns,
    ns_minikube,
    sub=False,
    exclude=aws_infrastructure.tasks.library.terraform.exclude_destroy_without_state(
        terraform_dir=TERRAFORM_DIR,
        exclude=[
            'init',
        ],
    )
)
