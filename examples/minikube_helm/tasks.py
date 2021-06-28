from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.minikube_helm
from invoke import Collection

# Key for configuration
CONFIG_KEY = 'examples_minikube_helm'

# Configure a collection
ns = Collection('minikube-helm')

ns.configure({
    CONFIG_KEY: {
        'working_dir': 'examples/minikube_helm',
        'bin_dir': '../../bin',
        'helm_charts_dir': '../../helm_repo',
        'instance_dirs': [
            'instance',
        ],
    }
})

# Define and import tasks
ns_minikube_helm = aws_infrastructure.tasks.library.minikube_helm.create_tasks(
    config_key=CONFIG_KEY,
    working_dir=ns.configuration()[CONFIG_KEY]['working_dir'],
    instance_dirs=ns.configuration()[CONFIG_KEY]['instance_dirs']
)

# Compose our collection
compose_collection(
    ns,
    ns_minikube_helm,
    sub=False,
    exclude=[
        'init',      # Task
        'output',    # Task
    ]
)
