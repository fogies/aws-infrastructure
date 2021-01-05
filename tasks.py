import os

import aws_infrastructure.task_templates.config
from invoke import Collection
from invoke import task
import packer_ami_minikube.tasks
import ruamel.yaml
import terraform_minikube_helm_example.tasks
import terraform_vpc_packer.tasks

# Build our task collection
ns = Collection()

# Tasks for Invoke configuration
ns_config = aws_infrastructure.task_templates.config.create_tasks()
ns.add_collection(ns_config)
ns.configure(ns_config.configuration())

# Tasks for ami-minikube
ns_packer_ami_minikube = packer_ami_minikube.tasks.ns
ns.add_collection(ns_packer_ami_minikube)
ns.configure(ns_packer_ami_minikube.configuration())

# Tasks for minikube-helm-example
ns_terraform_minikube_helm_example = terraform_minikube_helm_example.tasks.ns
ns.add_collection(ns_terraform_minikube_helm_example)
ns.configure(ns_terraform_minikube_helm_example.configuration())

# Tasks for vpc-packer
ns_terraform_vpc_packer = terraform_vpc_packer.tasks.ns
ns.add_collection(ns_terraform_vpc_packer)
ns.configure(ns_terraform_vpc_packer.configuration())

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

    # Package any chart which has a version that has not already been released
    for entry_current in os.scandir(helm_charts_dir):
        # Information about the chart that may need packaged
        # Using the existence of Chart.yaml to infer this is actually a chart
        path_chart = os.path.normpath(os.path.join(helm_charts_dir, entry_current.name, 'Chart.yaml'))
        if os.path.exists(path_chart) and os.path.isfile(path_chart):
            with open(path_chart) as file_chart:
                yaml_chart = ruamel.yaml.safe_load(file_chart)

            chart_name = yaml_chart['name']
            chart_version = yaml_chart['version']

            # Check existing releases of this same chart
            chart_released = False
            path_index = os.path.normpath(os.path.join(helm_repo_dir, 'index.yaml'))
            # Beware there might not be any prior index may exist
            if os.path.exists(path_index):
                with open(path_index) as file_index:
                    yaml_index = ruamel.yaml.safe_load(file_index)

                # Beware the prior index might not include this chart
                if chart_name in yaml_index['entries']:
                    for release_current in yaml_index['entries'][chart_name]:
                        if release_current['version'] == chart_version:
                            chart_released = True

            # If the current version was not previously released, go ahead with packaging it into staging
            if not chart_released:
                context.run(
                    command=' '.join([
                        bin_helm,
                        'package',
                        os.path.normpath(os.path.join(helm_charts_dir, entry_current.name)),
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

    # Build the release index, updating based on content of staging directory
    context.run(
        command=' '.join([
            bin_helm,
            'repo',
            'index',
            '"{}"'.format(helm_repo_staging_dir),
            '--merge "{}"'.format(os.path.normpath(os.path.join(helm_repo_dir, 'index.yaml')))
        ]),
    )

    # Move from staging into release
    for entry_current in os.scandir(helm_repo_staging_dir):
        if entry_current.name != '.gitignore':
            path_current_repo = os.path.normpath(os.path.join(helm_repo_dir, entry_current.name))
            path_current_repo_staging = os.path.normpath(os.path.join(helm_repo_staging_dir, entry_current.name))

            # The index will already exist
            if os.path.exists(path_current_repo):
                os.remove(path_current_repo)

            os.rename(path_current_repo_staging, path_current_repo)


@task
def helm_update(context):
    """
    Update chart dependencies.
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
