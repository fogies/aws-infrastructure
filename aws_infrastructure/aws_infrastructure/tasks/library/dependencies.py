"""
Tasks for ensuring project dependencies are installed.
"""

from collections import namedtuple
from invoke import Collection
from invoke import task
from pathlib import Path
from typing import Dict

Dependency = namedtuple('Dependency', ['pipfile_dirs', 'yarn_dirs'])


def _pipfile_lock(*, context, dependency_dir: Path):
    """
    Execute a pipenv lock, including development dependencies.
    """

    with context.cd(dependency_dir):
        context.run(
            command='pipenv lock --dev',
        )


def _pipfile_sync(*, context, dependency_dir: Path):
    """
    Execute a pipenv clean and sync, including development dependencies.
    """

    with context.cd(dependency_dir):
        # We also clean so that we don't accidentally have other packages installed,
        # which would likely cause failure in production where those are missing.

        context.run(
            command='pipenv sync --dev',
        )
        context.run(
            command='pipenv clean',
        )


def _yarn_install_frozen(*, context, dependency_dir: Path):
    """
    Execute a yarn install, keeping the lockfile frozen.
    """

    with context.cd(dependency_dir):
        context.run(
            command='yarn install --frozen-lockfile',
        )


def _yarn_upgrade(*, context, dependency_dir: Path):
    """
    Execute a yarn upgrade.
    """

    with context.cd(dependency_dir):
        context.run(
            command='yarn upgrade',
        )


def _task_install(*, dependency_name: str, dependency: Dependency):
    @task
    def install(context):
        """
        Install {} dependencies.
        """
        if dependency.pipfile_dirs:
            for dependency_dir in dependency.pipfile_dirs:
                _pipfile_sync(context=context, dependency_dir=Path(dependency_dir))
        if dependency.yarn_dirs:
            for dependency_dir in dependency.yarn_dirs:
                _yarn_install_frozen(context=context, dependency_dir=Path(dependency_dir))

    install.__doc__ = install.__doc__.format(dependency_name)

    return install


def _task_update(*, dependency_name: str, dependency: Dependency):
    @task
    def update(context):
        """
        Update {} dependencies.
        """
        if dependency.pipfile_dirs:
            for dependency_dir in dependency.pipfile_dirs:
                _pipfile_lock(context=context, dependency_dir=Path(dependency_dir))
        if dependency.yarn_dirs:
            for dependency_dir in dependency.yarn_dirs:
                _yarn_upgrade(context=context, dependency_dir=Path(dependency_dir))

    update.__doc__ = update.__doc__.format(dependency_name)

    return update


def create_tasks(
    *,
    config_key: str,
    dependencies: Dict[str, Dependency],
):
    ns = Collection('dependencies')

    ns_install = Collection('install')
    for (dependency_name_current, dependency_current) in dependencies.items():
        ns_install.add_task(
            _task_install(dependency_name=dependency_name_current, dependency=dependency_current),
            name=dependency_name_current
        )

    ns_update = Collection('update')
    for (dependency_name_current, dependency_current) in dependencies.items():
        ns_update.add_task(
            _task_update(dependency_name=dependency_name_current, dependency=dependency_current),
            name=dependency_name_current
        )

    ns.add_collection(ns_install, 'install')
    ns.add_collection(ns_update, 'update')

    return ns
