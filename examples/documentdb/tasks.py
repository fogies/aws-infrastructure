from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.documentdb
import aws_infrastructure.tasks.library.minikube
import aws_infrastructure.tasks.library.terraform
import aws_infrastructure.tasks.ssh
from invoke import Collection
from invoke import task
from pathlib import Path
from pymongo import MongoClient

CONFIG_KEY = 'examples_documentdb'
TERRAFORM_BIN = './bin/terraform.exe'
TERRAFORM_DIR = './examples/documentdb'
HELM_REPO_DIR = './helm_repo'
STAGING_LOCAL_HELMFILE_DIR = './.staging/helmfile'
STAGING_REMOTE_HELM_DIR = './.staging/helm'
STAGING_REMOTE_HELMFILE_DIR = './.staging/helmfile'

DOCUMENTDB_NAME = 'examples-documentdb'
INSTANCE_NAME = 'instance'

SSH_CONFIG_DIR = './examples/documentdb/{}'.format(INSTANCE_NAME)
SSH_CONFIG_PATH = '{}/ssh_config.yaml'.format(SSH_CONFIG_DIR)
DOCUMENTDB_CONFIG_DIR = './examples/documentdb/{}'.format(DOCUMENTDB_NAME)
DOCUMENTDB_CONFIG_PATH = '{}/documentdb_config.yaml'.format(DOCUMENTDB_CONFIG_DIR)

ns = Collection('documentdb')

# Compose from the DocumentDB and the Instance.
# Either would do a top-level apply and destroy, but both are augmented.
ns_combined = Collection('combined')

ns_documentdb = aws_infrastructure.tasks.library.documentdb.create_tasks(
    config_key=CONFIG_KEY,
    terraform_bin=TERRAFORM_BIN,
    terraform_dir=TERRAFORM_DIR,
    name=DOCUMENTDB_NAME,
)

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

destroy_post_exec_documentdb = aws_infrastructure.tasks.library.documentdb._destroy_post_exec(
    terraform_dir=Path(TERRAFORM_DIR),
    config_dir=Path(DOCUMENTDB_CONFIG_DIR),
)

destroy_post_exec_minikube = aws_infrastructure.tasks.library.minikube._destroy_post_exec(
    terraform_dir=Path(TERRAFORM_DIR),
    instance_names=[INSTANCE_NAME],
)


def destroy_post_exec_combined(*, context, params):
    destroy_post_exec_documentdb(context=context, params=params)
    destroy_post_exec_minikube(context=context, params=params)


ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
    config_key=CONFIG_KEY,
    terraform_bin=TERRAFORM_BIN,
    terraform_dir=TERRAFORM_DIR,

    destroy_post_exec=destroy_post_exec_combined
)


# Compose tasks from the combined Terraform
compose_collection(
    ns_combined,
    ns_terraform,
    sub=False,
    include=[
        'apply',
        'destroy',
    ]
)

# Compose tasks from the DocumentDB
compose_collection(
    ns_combined,
    ns_documentdb,
    sub=False,
    include=[
    ],
)

# Compose tasks from the instance
compose_collection(
    ns_combined,
    ns_minikube,
    sub=True,
    name='instance',
    include=[
    ],
)


@task
def ping(context):
    """
    Open a client and ping the database.
    """

    ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(SSH_CONFIG_PATH)
    documentdb_config = aws_infrastructure.tasks.library.documentdb.DocumentDBConfig.load(DOCUMENTDB_CONFIG_PATH)

    with aws_infrastructure.tasks.ssh.SSHClientContextManager(
        ssh_config=ssh_config,
    ) as ssh_client:
        with aws_infrastructure.tasks.ssh.SSHPortForwardContextManager(
                ssh_client=ssh_client,
                remote_host=documentdb_config.endpoint,
                remote_port=documentdb_config.port,
        ) as ssh_port_forward:
            client = MongoClient(
                host=[
                    'localhost'
                ],
                port=ssh_port_forward.local_port,
                connect=True,
                username=documentdb_config.admin_user,
                password=documentdb_config.admin_password,
                tls=True,
                tlsInsecure=True,
            )

            print(client.admin.command('ping'))


ns_combined.add_task(ping, 'ping')

# Compose our actual collection from the combined collection
compose_collection(
    ns,
    ns_combined,
    sub=False,
    exclude=aws_infrastructure.tasks.library.terraform.exclude_without_state(
        terraform_dir=TERRAFORM_DIR,
        exclude=[
        ],
        exclude_without_state=[
            'destroy',
            'ping',
        ]
    )
)
