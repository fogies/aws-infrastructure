from invoke import Collection
from invoke import task
import os
import ruamel.yaml

import aws_infrastructure.task_templates.config

import packer_ami_minikube
import terraform_minikube_helm_example
import terraform_vpc_packer

ns = Collection()

# Tasks in a 'tasks' collection

ns_tasks = Collection()
ns_tasks.add_task(aws_infrastructure.task_templates.config.template_config())
ns.add_collection(ns_tasks, name='tasks')
ns.configure(ns_tasks.configuration())

# Tasks in each of our included packages

ns.add_collection(packer_ami_minikube.ns, name='ami-minikube')
ns.configure(packer_ami_minikube.ns.configuration())

ns.add_collection(terraform_minikube_helm_example.ns, name='minikube-helm-example')
ns.configure(terraform_minikube_helm_example.ns.configuration())

ns.add_collection(terraform_vpc_packer.ns, name='vpc-packer')
ns.configure(terraform_vpc_packer.ns.configuration())

################################################################################
# Helm tasks including here until a refactoring to better locate them
################################################################################

HELM_CONFIG_KEY = 'helm'


@task
def helm_package(context):
    """
    Build packages from charts into staging.
    """

    config = context.config[HELM_CONFIG_KEY]

    bin_helm = os.path.normpath(os.path.join(config.bin_dir, 'helm.exe'))
    helm_charts_dir = os.path.normpath(config.helm_charts_dir)
    helm_repo_staging_dir = os.path.normpath(config.helm_repo_staging_dir)
    helm_repo_dir = os.path.normpath(config.helm_repo_dir)

    # Information about the chart we're trying to package
    path_chart = os.path.normpath(os.path.join(helm_charts_dir, 'ingress', 'Chart.yaml'))
    with open(path_chart) as file_chart:
        yaml_chart = ruamel.yaml.safe_load(file_chart)

    chart_name = yaml_chart['name']
    chart_version = yaml_chart['version']

    # Information about existing releases of that chart
    chart_released = False
    path_index = os.path.normpath(os.path.join(helm_repo_dir, 'index.yaml'))
    if os.path.exists(path_index):
        with open(path_index) as file_index:
            yaml_index = ruamel.yaml.safe_load(file_index)

        for release_current in yaml_index['entries'][chart_name]:
            if release_current['version'] == chart_version:
                chart_released = True

    if not chart_released:
        # Build the helm chart
        context.run(
            command=' '.join([
                bin_helm,
                'package',
                os.path.normpath(os.path.join(helm_charts_dir, 'ingress')),
                '--destination "{}"'.format(helm_repo_staging_dir)
            ]),
        )


@task
def helm_release(context):
    """
    Release staged packages.
    """

    config = context.config[HELM_CONFIG_KEY]

    bin_helm = os.path.normpath(os.path.join(config.bin_dir, 'helm.exe'))
    helm_repo_staging_dir = os.path.normpath(config.helm_repo_staging_dir)
    helm_repo_dir = os.path.normpath(config.helm_repo_dir)

    # Build the release index
    context.run(
        command=' '.join([
            bin_helm,
            'repo',
            'index',
            '"{}"'.format(helm_repo_staging_dir),
            '--merge "{}"'.format(os.path.normpath(os.path.join(helm_repo_dir, 'index.yaml')))
        ]),
    )

    # Move into the repo
    for file_current in os.listdir(helm_repo_staging_dir):
        if file_current != '.gitignore':
            path_current_repo = os.path.normpath(os.path.join(helm_repo_dir, file_current))
            path_current_repo_staging = os.path.normpath(os.path.join(helm_repo_staging_dir, file_current))

            if os.path.exists(path_current_repo):
                os.remove(path_current_repo)
            os.rename(path_current_repo_staging, path_current_repo)


@task
def helm_update(context):
    """
    Update charts.
    """

    config = context.config[HELM_CONFIG_KEY]

    bin_helm = os.path.normpath(os.path.join(config.bin_dir, 'helm.exe'))
    helm_charts_dir = os.path.normpath(config.helm_charts_dir)

    # Build the helm chart
    context.run(
        command=' '.join([
            bin_helm,
            'dependency',
            'update',
            os.path.normpath(os.path.join(helm_charts_dir, 'ingress')),
        ]),
    )


ns_helm = Collection()

ns_helm.configure({
    HELM_CONFIG_KEY: {
        'bin_dir': 'bin',
        'helm_charts_dir': 'helm',
        'helm_repo_dir': 'helm_repo',
        'helm_repo_staging_dir': 'helm_repo_staging',
    }
})


ns_helm.add_task(helm_package, 'package')
ns_helm.add_task(helm_release, 'release')
ns_helm.add_task(helm_update, 'update')

ns.add_collection(ns_helm, name='helm')
ns.configure(ns_helm.configuration())
