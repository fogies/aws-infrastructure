import os

from invoke import Collection
from invoke import task
import ruamel.yaml


def task_package(
    *,
    config_key: str
):
    """
    Create a task to build packages from charts into staging.
    """

    @task
    def package(context):
        """
        Build packages from charts into staging.
        """

        config = context.config[config_key]

        bin_helm = os.path.normpath(os.path.join(config.bin_dir, 'helm.exe'))
        helm_charts_dir = os.path.normpath(config.helm_charts_dir)
        helm_repo_staging_dir = os.path.normpath(config.helm_repo_staging_dir)
        helm_repo_dir = os.path.normpath(config.helm_repo_dir)

        # Package any chart which has a version that has not already been released
        for entry_current in os.scandir(helm_charts_dir):
            # Use the existence of Chart.yaml to infer this is actually a chart
            path_chart = os.path.normpath(os.path.join(helm_charts_dir, entry_current.name, 'Chart.yaml'))
            if os.path.exists(path_chart) and os.path.isfile(path_chart):
                # Get information about the chart that may need packaged
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

    return package


def task_release(
    *,
    config_key: str
):
    """
    Create a task to release staged packages.
    """

    @task
    def release(context):
        """
        Release staged packages.
        """

        config = context.config[config_key]

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

    return release


def task_update(
    *,
    config_key: str
):
    @task
    def update(context):
        """
        Update chart dependencies.
        """

        config = context.config[config_key]

        bin_helm = os.path.normpath(os.path.join(config.bin_dir, 'helm.exe'))
        helm_charts_dir = os.path.normpath(config.helm_charts_dir)

        # Update every chart
        for entry_current in os.scandir(helm_charts_dir):
            # Use the existence of Chart.yaml to infer this is actually a chart
            path_chart = os.path.normpath(os.path.join(helm_charts_dir, entry_current.name, 'Chart.yaml'))
            if os.path.exists(path_chart) and os.path.isfile(path_chart):
                # Update the chart
                context.run(
                    command=' '.join([
                        bin_helm,
                        'dependency',
                        'update',
                        os.path.normpath(os.path.join(helm_charts_dir, entry_current.name)),
                    ])
                )

    return update


def create_tasks(
    *,
    config_key: str,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    ns = Collection('helm')

    package = task_package(
        config_key=config_key
    )
    ns.add_task(package)

    release = task_release(
        config_key=config_key
    )
    ns.add_task(release)

    update = task_update(
        config_key=config_key
    )
    ns.add_task(update)

    return ns
