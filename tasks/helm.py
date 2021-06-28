"""
Tasks for managing Helm charts.
"""

from invoke import Collection

from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.helm

# Key for configuration
CONFIG_KEY = 'helm'

# Configure a collection
ns = Collection('helm')

ns.configure({
    CONFIG_KEY: {
        'bin_dir': 'bin',
        'helm_charts_dir': 'helm',
        'helm_repo_dir': 'helm_repo',
        'helm_repo_staging_dir': 'helm_repo_staging',
    }
})

# Define and import tasks
ns_helm = aws_infrastructure.tasks.library.helm.create_tasks(
    config_key=CONFIG_KEY
)

# Compose the collection
compose_collection(ns, ns_helm, sub=False)
