from invoke import Collection
from invoke import task
import os
from pathlib import Path
import ruamel.yaml
from typing import List
from typing import Union


def _task_package(
    *,
    config_key: str,
    bin_helm: Path,
    dirs_helm_charts: List[Path],
    dir_helm_repo: Path,
    dir_helm_repo_staging: Path,
):
    """
    Create a task to build packages from charts into staging.
    """

    @task
    def package(context):
        """
        Build packages from charts into staging.
        """

        # Go through provided helm charts directories
        for dir_helm_charts_current in dirs_helm_charts:
            # Package any chart which has a version that has not already been released
            for entry_current in os.scandir(dir_helm_charts_current):
                # Use the existence of Chart.yaml to infer this is actually a chart
                path_chart = Path(dir_helm_charts_current, entry_current.name, 'Chart.yaml')
                if path_chart.exists():
                    # Get information about the chart that may need packaged
                    with open(path_chart) as file_chart:
                        yaml_chart = ruamel.yaml.safe_load(file_chart)

                    chart_name = yaml_chart['name']
                    chart_version = yaml_chart['version']

                    # Check existing releases of this same chart
                    chart_released = False
                    path_index = Path(dir_helm_repo, 'index.yaml')
                    # Beware there might not be any prior index
                    if path_index.exists():
                        with open(path_index) as file_index:
                            yaml_index = ruamel.yaml.safe_load(file_index)

                        # Beware the prior index might not include this chart
                        if chart_name in yaml_index['entries']:
                            for release_current in yaml_index['entries'][chart_name]:
                                if release_current['version'] == chart_version:
                                    chart_released = True

                    # If the current version was not previously released, go ahead with packaging it into staging
                    if not chart_released:
                        # Ensure dependencies are current
                        context.run(
                            command=' '.join([
                                str(bin_helm),
                                'dependency',
                                'update',
                                '"{}"'.format(Path(dir_helm_charts_current, entry_current.name)),
                            ])
                        )

                        # Do the actual packaging
                        context.run(
                            command=' '.join([
                                str(bin_helm),
                                'package',
                                '"{}"'.format(Path(dir_helm_charts_current, entry_current.name)),
                                '--destination "{}"'.format(dir_helm_repo_staging)
                            ]),
                        )

    return package


def _task_release(
    *,
    config_key: str,
    bin_helm: Path,
    dir_helm_repo: Path,
    dir_helm_repo_staging: Path,
):
    """
    Create a task to release staged packages.
    """

    @task
    def release(context):
        """
        Release staged packages.
        """

        # Build the release index, updating based on content of staging directory
        context.run(
            command=' '.join([
                str(bin_helm),
                'repo',
                'index',
                '"{}"'.format(dir_helm_repo_staging),
                '--merge "{}"'.format(Path(dir_helm_repo, 'index.yaml'))
            ]),
        )

        # Move from staging into release
        for entry_current in os.scandir(dir_helm_repo_staging):
            if entry_current.name != '.gitignore':
                path_current_repo = Path(dir_helm_repo, entry_current.name)
                path_current_repo_staging = Path(dir_helm_repo_staging, entry_current.name)

                # The index will already exist
                if path_current_repo.exists():
                    os.remove(path_current_repo)

                os.rename(path_current_repo_staging, path_current_repo)

    return release


def create_tasks(
    *,
    config_key: str,
    bin_helm: Union[Path, str],
    dirs_helm_charts: List[Union[Path, str]],
    dir_helm_repo: Union[Path, str],
    dir_helm_repo_staging: Union[Path, str],
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    bin_helm = Path(bin_helm)
    dirs_helm_charts = [Path(dir_helm_charts_current) for dir_helm_charts_current in dirs_helm_charts]
    dir_helm_repo = Path(dir_helm_repo)
    dir_helm_repo_staging = Path(dir_helm_repo_staging)

    ns = Collection('helm')

    package = _task_package(
        config_key=config_key,
        bin_helm=bin_helm,
        dirs_helm_charts=dirs_helm_charts,
        dir_helm_repo=dir_helm_repo,
        dir_helm_repo_staging=dir_helm_repo_staging,
    )
    ns.add_task(package)

    release = _task_release(
        config_key=config_key,
        bin_helm=bin_helm,
        dir_helm_repo=dir_helm_repo,
        dir_helm_repo_staging=dir_helm_repo_staging,
    )
    ns.add_task(release)

    return ns
