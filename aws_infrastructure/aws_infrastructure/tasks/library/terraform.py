import json
import os
from typing import List

from invoke import Collection
from invoke import task


def task_init(
    *,
    config_key: str
):
    """
    Create a task to initialize Terraform and update any dependencies.
    """

    @task
    def init(context):
        """
        Initialize Terraform and update any dependencies.
        """

        config = context.config[config_key]
        working_dir = os.path.normpath(config.working_dir)
        bin_terraform = os.path.normpath(os.path.join(config.bin_dir, 'terraform.exe'))

        with context.cd(working_dir):
            print('Terraform initializing')
            context.run(
                command=' '.join([
                    bin_terraform,
                    'init',
                    '-no-color',
                ]),
            )
            context.run(
                command=' '.join([
                    bin_terraform,
                    'get',
                    '-update',
                    '-no-color',
                ]),
            )

    return init


def task_apply(
    *,
    config_key: str,
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

        config = context.config[config_key]
        working_dir = os.path.normpath(config.working_dir)
        bin_terraform = os.path.normpath(os.path.join(config.bin_dir, 'terraform.exe'))

        variables_dict = variables(context=context) if variables else {}

        with context.cd(working_dir):
            print('Terraform applying')
            context.run(
                command=' '.join([
                    bin_terraform,
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


def task_destroy(
    *,
    config_key: str,
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

        config = context.config[config_key]
        working_dir = os.path.normpath(config.working_dir)
        bin_terraform = os.path.normpath(os.path.join(config.bin_dir, 'terraform.exe'))

        variables_dict = variables(context=context) if variables else {}

        with context.cd(working_dir):
            print('Terraform destroying')
            context.run(
                command=' '.join([
                    bin_terraform,
                    'destroy',
                    ' '.join([
                        '-var "{}={}"'.format(key, value) for (key, value) in variables_dict.items()
                    ]),
                    '-auto-approve',
                    '-no-color',
                ]),
            )

    return destroy


def task_output(
    *,
    config_key: str,
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

        config = context.config[config_key]
        working_dir = os.path.normpath(config.working_dir)
        bin_terraform = os.path.normpath(os.path.join(config.bin_dir, 'terraform.exe'))

        with context.cd(working_dir):
            print('Obtaining Terraform output')
            result = context.run(
                command=' '.join([
                    bin_terraform,
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

    ns = Collection('terraform')

    init = task_init(
        config_key=config_key
    )
    ns.add_task(init)

    apply = task_apply(
        config_key=config_key,
        init=init,
        variables=variables,
        pre=apply_pre,
        post=apply_post
    )
    ns.add_task(apply)

    destroy = task_destroy(
        config_key=config_key,
        init=init,
        variables=variables,
        pre=destroy_pre,
        post=destroy_post
    )
    ns.add_task(destroy)

    if output_tuple_factory:
        output = task_output(
            config_key=config_key,
            init=init,
            output_tuple_factory=output_tuple_factory
        )
        ns.add_task(output)

    return ns


def create_context_manager(
    *,
    init: task,
    apply: task = None,
    output: task = None,
    destroy: task = None
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
            if apply:
                apply(self._context)

            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if destroy:
                destroy(self._context)

        @property
        def output(self):
            if self._cached_output is None:
                self._cached_output = output(self._context)

            return self._cached_output

    return terraform_context_manager
