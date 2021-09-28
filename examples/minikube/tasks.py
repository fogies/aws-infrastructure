from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.instance_helmfile
import aws_infrastructure.tasks.library.minikube
import aws_infrastructure.tasks.library.terraform
from invoke import Collection
from pathlib import Path

CONFIG_KEY = 'examples_minikube'
BIN_TERRAFORM = './bin/terraform.exe'
DIR_TERRAFORM = './examples/minikube'
DIR_HELM_REPO = './helm_repo'
DIR_STAGING_LOCAL_HELMFILE = './.staging/helmfile'
INSTANCE_NAMES = ['instance']

ns = Collection('minikube')

ns_minikube = aws_infrastructure.tasks.library.minikube.create_tasks(
    config_key=CONFIG_KEY,
    bin_terraform=BIN_TERRAFORM,
    dir_terraform=DIR_TERRAFORM,
    dir_helm_repo=DIR_HELM_REPO,
    dir_staging_local_helmfile=DIR_STAGING_LOCAL_HELMFILE,
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


def examples_nginx_values_variables(*, context):
    return {
        'exampleHelmNginxText': 'Example Helm Nginx Text from examples_nginx_values_variables.'
    }


for instance_name_current in INSTANCE_NAMES:
    path_ssh_config = Path(DIR_TERRAFORM, instance_name_current, 'ssh_config.yaml')

    if path_ssh_config.exists():
        task_helmfile_nginx = aws_infrastructure.tasks.library.instance_helmfile.task_helmfile_apply(
            config_key=CONFIG_KEY,
            path_ssh_config=path_ssh_config,
            dir_staging_local=DIR_STAGING_LOCAL_HELMFILE,
            path_helmfile='./examples/helmfile_nginx/helmfile.yaml',
            path_helmfile_config='./examples/helmfile_nginx/helmfile-config.yaml',
            values_variables={
                'examples_nginx': examples_nginx_values_variables
            },
        )

        ns.add_task(task_helmfile_nginx, name='helmfile-nginx')
