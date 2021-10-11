from collections import namedtuple
from invoke import Collection
from invoke import task
import json
import os
from pathlib import Path
from typing import List
from typing import Union


def _write_terraform_variables(
    *,
    terraform_variables_path: Path,
    terraform_variables_dict,
):
    with open(terraform_variables_path, 'w') as file_variables:
        file_variables.write('\n'.join(
            [
                '################################################################################',
                '# This file is automatically generated. Changes will be overwritten.',
                '################################################################################',
                '',
            ]
        ))
        for key, value in terraform_variables_dict.items():
            file_variables.write(
                '{} = {}\n'.format(
                    key,
                    json.dumps(value, separators=(',', ' = ')),
                )
            )

def _task_init(
    *,
    config_key: str,
    terraform_bin: Path,
    terraform_dir: Path,
):
    """
    Create a task to initialize Terraform and update any dependencies.
    """

    @task
    def init(context):
        """
        Initialize Terraform and update any dependencies.
        """

        with context.cd(terraform_dir):
            print('Terraform initializing')
            context.run(
                command=' '.join([
                    os.path.relpath(terraform_bin, terraform_dir),
                    'init',
                    '-no-color',
                ]),
            )
            context.run(
                command=' '.join([
                    os.path.relpath(terraform_bin, terraform_dir),
                    'get',
                    '-update',
                    '-no-color',
                ]),
            )

    return init


def _task_apply(
    *,
    config_key: str,
    terraform_bin: Path,
    terraform_dir: Path,
    terraform_variables_factory,
    terraform_variables_path: Path,
    init: task,
    pre_invoke: List[task],
    post_invoke: List[task],
    pre_exec,  # A function to execute before
    post_exec, # A function to execute after
):
    """
    Create a task to issue a Terraform apply.
    """

    pre_invoke_combined = [init]
    pre_invoke_combined.extend(pre_invoke or [])

    @task(
        pre=pre_invoke_combined,
        post=post_invoke
    )
    def apply(context):
        """
        Issue a Terraform apply.
        """

        terraform_variables_dict = {}
        if terraform_variables_factory:
            terraform_variables_dict = terraform_variables_factory(context=context)
            _write_terraform_variables(
                terraform_variables_path=terraform_variables_path,
                terraform_variables_dict=terraform_variables_dict,
            )

        if pre_exec:
            params = namedtuple(
                'apply_pre_exec',
                [
                    'terraform_variables',
                ]
            )(
                terraform_variables=terraform_variables_dict
            )
            pre_exec(context=context, params=params)

        with context.cd(terraform_dir):
            print('Terraform applying')
            context.run(
                command=' '.join(filter(None, [
                    os.path.relpath(terraform_bin, terraform_dir),
                    'apply',
                    '-var-file="{}"'.format(
                        os.path.relpath(terraform_variables_path, terraform_dir)
                    ) if terraform_variables_factory else None,
                    '-auto-approve',
                    '-no-color',
                ])),
                echo=True
            )

        if post_exec:
            params = namedtuple(
                'apply_post_exec',
                [
                    'terraform_variables',
                ]
            )(
                terraform_variables=terraform_variables_dict
            )
            post_exec(context=context, params=params)

    return apply


def _task_destroy(
    *,
    config_key: str,
    terraform_bin: Path,
    terraform_dir: Path,
    terraform_variables_factory,
    terraform_variables_path: Path,
    init: task,
    pre_invoke: List[task],
    post_invoke: List[task],
    pre_exec,  # A function to execute before
    post_exec, # A function to execute after
):
    """
    Create a task to issue a Terraform destroy.
    """

    pre_invoke_combined = [init]
    pre_invoke_combined.extend(pre_invoke or [])

    @task(
        pre=pre_invoke_combined,
        post=post_invoke
    )
    def destroy(context):
        """
        Issue a Terraform destroy.
        """

        terraform_variables_dict = {}
        if terraform_variables_factory:
            terraform_variables_dict = terraform_variables_factory(context=context)
            _write_terraform_variables(
                terraform_variables_path=terraform_variables_path,
                terraform_variables_dict=terraform_variables_dict,
            )

        if pre_exec:
            params = namedtuple(
                'destroy_pre_exec',
                [
                    'terraform_variables',
                ]
            )(
                terraform_variables=terraform_variables_dict
            )
            pre_exec(context=context, params=params)

        with context.cd(terraform_dir):
            print('Terraform destroying')
            context.run(
                command=' '.join(filter(None, [
                    os.path.relpath(terraform_bin, terraform_dir),
                    'destroy',
                    '-var-file="{}"'.format(
                        os.path.relpath(terraform_variables_path, terraform_dir)
                    ) if terraform_variables_factory else None,
                    '-auto-approve',
                    '-no-color',
                ])),
            )

        if post_exec:
            params = namedtuple(
                'destroy_post_exec',
                [
                    'terraform_variables',
                ]
            )(
                terraform_variables=terraform_variables_dict
            )
            post_exec(context=context, params=params)

    return destroy


def _task_output(
    *,
    config_key: str,
    terraform_bin: Path,
    terraform_dir: Path,
    init: task,
    output_tuple_factory,
    output_enhance = None, # A function to execute to enhance the output
):
    """
    Create a task to obtain Terraform output.
    """

    pre_invoke_combined = [init]

    @task(
        pre=pre_invoke_combined
    )
    def output(context):
        """
        Obtain Terraform output.
        """

        with context.cd(terraform_dir):
            print('Obtaining Terraform output')
            result = context.run(
                command=' '.join([
                    os.path.relpath(terraform_bin, terraform_dir),
                    'output',
                    '-json',
                    '-no-color',
                ]),
            )

        output_json = json.loads(result.stdout.strip())

        output_tuple = output_tuple_factory(**{key: output_json[key]['value'] for key in output_tuple_factory._fields})

        if output_enhance:
            return output_enhance(context=context, output=output_tuple)
        else:
            return output_tuple

    return output


def create_tasks(
    *,
    config_key: str,
    terraform_bin: Union[Path, str],
    terraform_dir: Union[Path, str],

    terraform_variables_factory = None,
    terraform_variables_path: Union[Path, str] = None,
    apply_pre_invoke: List[task] = None,
    apply_post_invoke: List[task] = None,
    apply_pre_exec=None,
    apply_post_exec=None,
    destroy_pre_invoke: List[task] = None,
    destroy_post_invoke: List[task] = None,
    destroy_pre_exec=None,
    destroy_post_exec=None,
    output_tuple_factory = None,
    output_enhance=None,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    terraform_bin = Path(terraform_bin)
    terraform_dir = Path(terraform_dir)
    terraform_variables_path = Path(terraform_variables_path) if terraform_variables_path else None

    if terraform_variables_factory is not None:
        if terraform_variables_path is None:
            raise ValueError('If terraform_variables_factory is provided, terraform_variables_path is required.')

    ns = Collection('terraform')

    init = _task_init(
        config_key=config_key,
        terraform_bin=terraform_bin,
        terraform_dir=terraform_dir,
    )
    ns.add_task(init)

    apply = _task_apply(
        config_key=config_key,
        terraform_bin=terraform_bin,
        terraform_dir=terraform_dir,
        terraform_variables_factory=terraform_variables_factory,
        terraform_variables_path=terraform_variables_path,
        init=init,
        pre_invoke=apply_pre_invoke,
        post_invoke=apply_post_invoke,
        pre_exec=apply_pre_exec,
        post_exec=apply_post_exec,
    )
    ns.add_task(apply)

    destroy = _task_destroy(
        config_key=config_key,
        terraform_bin=terraform_bin,
        terraform_dir=terraform_dir,
        terraform_variables_factory=terraform_variables_factory,
        terraform_variables_path=terraform_variables_path,
        init=init,
        pre_invoke=destroy_pre_invoke,
        post_invoke=destroy_post_invoke,
        pre_exec=destroy_pre_exec,
        post_exec=destroy_post_exec,
    )
    ns.add_task(destroy)

    if output_tuple_factory:
        output = _task_output(
            config_key=config_key,
            terraform_bin=terraform_bin,
            terraform_dir=terraform_dir,
            init=init,
            output_tuple_factory=output_tuple_factory,
            output_enhance=output_enhance,
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

    output_enhance = None,
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
    terraform_dir: Union[Path, str],
    exclude: List[str],
) -> List[str]:
    """
    Helper for excluding the 'destroy' task if there is no current Terraform state.
    """

    # Ensure Path object
    terraform_dir = Path(terraform_dir)

    # Determine whether state exists
    state_exists = True

    # Confirm the state file exists
    if state_exists:
        path_state = Path(terraform_dir, 'terraform.tfstate')
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
