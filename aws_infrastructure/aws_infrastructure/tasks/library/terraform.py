from invoke import Collection
from invoke import task
import json
import os
from pathlib import Path
from typing import List
from typing import Union


def _task_init(
    *,
    config_key: str,
    bin_terraform: Path,
    dir_terraform: Path,
):
    """
    Create a task to initialize Terraform and update any dependencies.
    """

    @task
    def init(context):
        """
        Initialize Terraform and update any dependencies.
        """

        with context.cd(dir_terraform):
            print('Terraform initializing')
            context.run(
                command=' '.join([
                    os.path.relpath(bin_terraform, dir_terraform),
                    'init',
                    '-no-color',
                ]),
            )
            context.run(
                command=' '.join([
                    os.path.relpath(bin_terraform, dir_terraform),
                    'get',
                    '-update',
                    '-no-color',
                ]),
            )

    return init


def _task_apply(
    *,
    config_key: str,
    bin_terraform: Path,
    dir_terraform: Path,
    init: task,
    variables=None,
    pre: List[task] = None,
    post: List[task] = None
):
    """
    Create a task to issue a Terraform apply.
    """

    pre_combined = [init]
    pre_combined.extend(pre or [])

    @task(
        pre=pre_combined,
        post=post
    )
    def apply(context):
        """
        Issue a Terraform apply.
        """

        variables_dict = variables(context=context) if variables else {}

        with context.cd(dir_terraform):
            print('Terraform applying')
            context.run(
                command=' '.join([
                    os.path.relpath(bin_terraform, dir_terraform),
                    'apply',
                    ' '.join([
                        '-var "{}={}"'.format(key, value) for (key, value) in variables_dict.items()
                    ]),
                    '-auto-approve',
                    '-no-color',
                ]),
                echo=True
            )

    return apply


def _task_destroy(
    *,
    config_key: str,
    bin_terraform: Path,
    dir_terraform: Path,
    init: task,
    variables=None,
    pre: List[task] = None,
    post: List[task] = None
):
    """
    Create a task to issue a Terraform destroy.
    """

    pre_combined = [init]
    pre_combined.extend(pre or [])

    @task(
        pre=pre_combined,
        post=post
    )
    def destroy(context):
        """
        Issue a Terraform destroy.
        """

        variables_dict = variables(context=context) if variables else {}

        with context.cd(dir_terraform):
            print('Terraform destroying')
            context.run(
                command=' '.join([
                    os.path.relpath(bin_terraform, dir_terraform),
                    'destroy',
                    ' '.join([
                        '-var "{}={}"'.format(key, value) for (key, value) in variables_dict.items()
                    ]),
                    '-auto-approve',
                    '-no-color',
                ]),
            )

    return destroy


def _task_output(
    *,
    config_key: str,
    bin_terraform: Path,
    dir_terraform: Path,
    init: task,
    output_tuple_factory
):
    """
    Create a task to obtain Terraform output.
    """

    pre_combined = [init]

    @task(
        pre=pre_combined
    )
    def output(context):
        """
        Obtain Terraform output.
        """

        with context.cd(dir_terraform):
            print('Obtaining Terraform output')
            result = context.run(
                command=' '.join([
                    os.path.relpath(bin_terraform, dir_terraform),
                    'output',
                    '-json',
                    '-no-color',
                ]),
            )

        output_json = json.loads(result.stdout.strip())

        output_tuple = output_tuple_factory(**{key: output_json[key]['value'] for key in output_tuple_factory._fields})

        return output_tuple

    return output


def create_tasks(
    *,
    config_key: str,
    bin_terraform: Union[Path, str],
    dir_terraform: Union[Path, str],

    variables=None,
    apply_pre: List[task] = None,
    apply_post: List[task] = None,
    destroy_pre: List[task] = None,
    destroy_post: List[task] = None,
    output_tuple_factory=None,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    bin_terraform = Path(bin_terraform)
    dir_terraform = Path(dir_terraform)

    ns = Collection('terraform')

    init = _task_init(
        config_key=config_key,
        bin_terraform=bin_terraform,
        dir_terraform=dir_terraform,
    )
    ns.add_task(init)

    apply = _task_apply(
        config_key=config_key,
        bin_terraform=bin_terraform,
        dir_terraform=dir_terraform,
        init=init,
        variables=variables,
        pre=apply_pre,
        post=apply_post
    )
    ns.add_task(apply)

    destroy = _task_destroy(
        config_key=config_key,
        bin_terraform=bin_terraform,
        dir_terraform=dir_terraform,
        init=init,
        variables=variables,
        pre=destroy_pre,
        post=destroy_post
    )
    ns.add_task(destroy)

    if output_tuple_factory:
        output = _task_output(
            config_key=config_key,
            bin_terraform=bin_terraform,
            dir_terraform=dir_terraform,
            init=init,
            output_tuple_factory=output_tuple_factory
        )
        ns.add_task(output)

    return ns


def create_context_manager(
    *,
    init: task,
    apply: task,
    output: task,
    destroy: task,
):
    """
    Create a context manager.
    """

    class terraform_context_manager:
        """
        Context manager for initializing, creating, obtaining output from, and destroying a Terraform resource.
        """

        def __init__(self, context):
            self._context = context
            self._cached_output = None

            init(self._context)

        def __enter__(self):
            apply(self._context)

            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            destroy(self._context)

        @property
        def output(self):
            if self._cached_output is None:
                self._cached_output = output(self._context)

            return self._cached_output

    return terraform_context_manager


def create_context_manager_read_only(
    *,
    init: task,
    output: task,
):
    """
    Create a context manager limited to only accessing output.
    """

    class terraform_context_manager_read_only:
        """
        Context manager for initializing and obtaining output from a Terraform resource.
        """

        def __init__(self, context):
            self._context = context
            self._cached_output = None

            init(self._context)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        @property
        def output(self):
            if self._cached_output is None:
                self._cached_output = output(self._context)

            return self._cached_output

    return terraform_context_manager_read_only


def exclude_destroy_without_state(
    *,
    dir_terraform: Union[Path, str],
    exclude: List[str],
) -> List[str]:
    """
    Helper for excluding the 'destroy' task if there is no current Terraform state.
    """

    # Ensure Path object
    dir_terraform = Path(dir_terraform)

    # Determine whether state exists
    state_exists = True

    # Confirm the state file exists
    if state_exists:
        path_state = Path(dir_terraform, 'terraform.tfstate')
        if not path_state.exists():
            state_exists = False

    # Confirm the state file is not empty
    if state_exists:
        with open(path_state, mode='r') as file_state:
            json_state = json.load(file_state)
        if json_state['resources'] == []:
            state_exists = False

    # If no state exists, append 'destroy' to the provided exclude list
    if not state_exists:
        exclude = list(exclude)
        exclude.append('destroy')

    return exclude
