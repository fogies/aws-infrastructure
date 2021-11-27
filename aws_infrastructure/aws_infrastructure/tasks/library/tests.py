"""
Tasks for executing tests within appropriate environments.
"""

from dataclasses import dataclass
from invoke import Collection
from invoke import task
from pathlib import Path
from typing import Dict
from typing import List
from typing import Union


@dataclass(frozen=True)
class Test:
    pipenv_pytest_dirs: List[Union[Path, str]]


def _pipenv_pytest(*, context, test_dir: Path):
    """
    Execute pytest within a Pipenv.
    """

    with context.cd(test_dir):
        context.run(
            command='pipenv run pytest',
        )


def _task_test(*, test_name: str, test: Test):
    @task
    def test(context):
        """
        Execute {} tests.
        """
        if test.pipenv_pytest_dirs:
            for test_dir in test.pipenv_pytest_dirs:
                _pipenv_pytest(context=context, test_dir=test_dir)

    test.__doc__ = test.__doc__.format(test_name)

    return test


def create_tasks(
    *,
    config_key: str,
    tests: Dict[str, Test],
):
    ns = Collection('test')

    for (test_name_current, test_current) in tests.items():
        ns.add_task(
            _task_test(test_name=test_name_current, test=test_current),
            name=test_name_current,
        )

    return ns
