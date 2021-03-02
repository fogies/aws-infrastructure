import aws_infrastructure.task_templates.minikube_helm
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
minikube_helm_tasks = aws_infrastructure.task_templates.minikube_helm.create_tasks(
    config_key=CONFIG_KEY,
    working_dir=ns.configuration()[CONFIG_KEY]['working_dir'],
    instance_dirs=ns.configuration()[CONFIG_KEY]['instance_dirs']
)

# Add tasks to our collection
# - Exclude 'init' and 'output' for legibility, could be enabled for debugging.
# - Include collections that contain tasks for created instances.
for task_current in minikube_helm_tasks.tasks.values():
    if task_current.name in ['init', 'output']:
        continue

    ns.add_task(task_current)

# Add child collections to our collection
# - Promote tasks from the 'instance' collection to our collection
for collection_current in minikube_helm_tasks.collections.values():
    if collection_current.name == 'instance':
        for task_current in collection_current.tasks.values():
            ns.add_task(task_current)

        continue

    ns.add_collection(collection_current)
