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
class TestConfig:
    pipenv_pytest_dirs: List[Union[Path, str]]


def _pipenv_pytest(*, context, test_dir: Path, verbose: int, keyword: str):
    """
    Execute pytest within a Pipenv.
    """

    with context.cd(test_dir):
        # Enforce a minimum verbosity of 1
        verbose = verbose + 1
        arg_verbose = "-{} ".format("v" * verbose)

        # Pass through any keyword argument
        arg_keyword = ""
        if keyword:
            arg_keyword = '-k "{}" '.format(keyword)

        # Combine all args
        command_args = "{}{}{}".format(
            "-rsx ",  # Report (s)kipped and (f)ailed tests
            arg_verbose,
            arg_keyword,
        )

        context.run(
            command="pipenv run pytest {}".format(command_args),
            # If multiple test sessions are to be executed,
            # continue despite a failure in this test session
            warn=True,
        )


def _task_test(*, test_name: str, test_config: TestConfig):
    @task(incrementable=["verbose"])
    def test(context, verbose=0, keyword=None):
        """
        Execute {} tests.
        """
        if test_config.pipenv_pytest_dirs:
            for test_dir in test_config.pipenv_pytest_dirs:
                _pipenv_pytest(
                    context=context,
                    test_dir=test_dir,
                    verbose=verbose,
                    keyword=keyword,
                )

    test.__doc__ = test.__doc__.format(test_name)

    return test


def create_tasks(
    *,
    config_key: str,
    test_configs: Dict[str, TestConfig],
):
    ns = Collection("test")

    for (test_name_current, test_config_current) in test_configs.items():
        ns.add_task(
            _task_test(test_name=test_name_current, test_config=test_config_current),
            name=test_name_current,
        )

    return ns
