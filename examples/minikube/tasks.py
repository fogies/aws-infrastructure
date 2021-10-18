from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.instance_helmfile
import aws_infrastructure.tasks.library.minikube
import aws_infrastructure.tasks.library.terraform
from invoke import Collection
from pathlib import Path

CONFIG_KEY = 'examples_minikube'
TERRAFORM_BIN = './bin/terraform.exe'
TERRAFORM_DIR = './examples/minikube'
HELM_REPO_DIR = './helm_repo'
STAGING_LOCAL_HELMFILE_DIR = './.staging/helmfile'
STAGING_REMOTE_HELM_DIR = './.staging/helm'
STAGING_REMOTE_HELMFILE_DIR = './.staging/helmfile'
INSTANCE_NAME = 'instance'

ns = Collection('minikube')

ns_minikube = aws_infrastructure.tasks.library.minikube.create_tasks(
    config_key=CONFIG_KEY,
    terraform_bin=TERRAFORM_BIN,
    terraform_dir=TERRAFORM_DIR,
    helm_repo_dir=HELM_REPO_DIR,
    staging_local_helmfile_dir=STAGING_LOCAL_HELMFILE_DIR,
    staging_remote_helm_dir=STAGING_REMOTE_HELM_DIR,
    staging_remote_helmfile_dir=STAGING_REMOTE_HELMFILE_DIR,
    instance_names=[INSTANCE_NAME],
)


def examples_nginx_values_factory(*, context):
    return {
        'exampleHelmNginxText': 'Example Helm Nginx Text from examples_nginx_values_variables.'
    }


ssh_config_path = Path(TERRAFORM_DIR, INSTANCE_NAME, 'ssh_config.yaml')

task_helmfile_nginx = aws_infrastructure.tasks.library.instance_helmfile.task_helmfile_apply(
    config_key=CONFIG_KEY,
    ssh_config_path=ssh_config_path,
    staging_local_dir=STAGING_LOCAL_HELMFILE_DIR,
    staging_remote_dir=STAGING_REMOTE_HELMFILE_DIR,
    path_helmfile='./examples/helmfile_nginx/helmfile.yaml',
    path_helmfile_config='./examples/helmfile_nginx/helmfile-config.yaml',
    helmfile_values_factories={
        'examples_nginx': examples_nginx_values_factory
    },
)

ns_minikube.add_task(task_helmfile_nginx, name='helmfile-nginx')

compose_collection(
    ns,
    ns_minikube,
    sub=False,
    exclude=aws_infrastructure.tasks.library.terraform.exclude_without_state(
        terraform_dir=TERRAFORM_DIR,
        exclude=[
            'init',
        ],
        exclude_without_state=[
            'destroy',
            'helmfile-nginx',
        ],
    )
)
