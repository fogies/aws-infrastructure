"""
Tasks for managing Helm charts.
"""

from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.helm
from invoke import Collection

CONFIG_KEY = 'helm'
BIN_HELM = './bin/helm.exe'
DIRS_HELM_CHARTS = [
    './helm',
    './examples',
]
DIR_HELM_REPO = './helm_repo'
DIR_HELM_REPO_STAGING = './helm_repo_staging'

ns = Collection('helm')

ns_helm = aws_infrastructure.tasks.library.helm.create_tasks(
    config_key=CONFIG_KEY,
    bin_helm=BIN_HELM,
    dirs_helm_charts=DIRS_HELM_CHARTS,
    dir_helm_repo=DIR_HELM_REPO,
    dir_helm_repo_staging=DIR_HELM_REPO_STAGING,
)

compose_collection(
    ns,
    ns_helm,
    sub=False
)
