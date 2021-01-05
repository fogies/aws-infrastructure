import aws_infrastructure.task_templates.minikube_helm
from invoke import Collection

# Key for configuration
CONFIG_KEY = 'terraform_minikube_helm_example'

# Configure a collection
ns = Collection('minikube-helm-example')

ns.configure({
    CONFIG_KEY: {
        'working_dir': 'terraform_minikube_helm_example',
        'bin_dir': '../bin',
        'helm_charts_dir': '../helm_repo',
        'instance_dirs': [
            'instance_1',
            'instance_2'
        ]
    }
})


# Define and import tasks
minikube_helm_tasks = aws_infrastructure.task_templates.minikube_helm.create_tasks(
    config_key=CONFIG_KEY,
    working_dir=ns.configuration()[CONFIG_KEY]['working_dir'],
    instance_dirs=ns.configuration()[CONFIG_KEY]['instance_dirs']
)


# Add tasks to collection
# - Exclude 'init' and 'output' for legibility, could be enabled for debugging.
# - Include collections that contain tasks for created instances.
for task_current in minikube_helm_tasks.tasks.values():
    if task_current.name in ['init', 'output']:
        continue

    ns.add_task(task_current)

for collection_current in minikube_helm_tasks.collections.values():
    ns.add_collection(collection_current)
