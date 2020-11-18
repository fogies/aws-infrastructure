from invoke.tasks import task
import json
import os
from typing import List


def template_init(
    *,
    config_key: str
):
    """
    Template for a task to initialize Terraform and update any dependencies.
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

    return init


def template_apply(
    *,
    config_key: str,
    init: task,
    pre: List[task] = None,
    post: List[task] = None
):
    """
    Template for a task to issue a Terraform apply.
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

        with context.cd(working_dir):
            print('Terraform applying')
            context.run(
                command=' '.join([
                    bin_terraform,
                    'apply',
                    '-auto-approve',
                    '-no-color',
                ]),
            )

    return apply


def template_destroy(
    *,
    config_key: str,
    init: task,
    pre: List[task] = None,
    post: List[task] = None
):
    """
    Template for a task to issue a Terraform destroy.
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

        with context.cd(working_dir):
            print('Terraform destroying')
            context.run(
                command=' '.join([
                    bin_terraform,
                    'destroy',
                    '-auto-approve',
                    '-no-color',
                ]),
            )

    return destroy


def template_output(
    *,
    config_key: str,
    init: task,
    output_tuple_factory,
    pre: List[task] = None,
    post: List[task] = None
):
    """
    Template for a task to obtain Terraform output.
    """

    pre_combined = [init]
    pre_combined.extend(pre or [])

    @task(
        pre=pre_combined,
        post=post
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


def template_context_manager(
    *,
    init: task = None,
    apply: task = None,
    output: task = None,
    destroy: task = None
):
    """
    Template to create a context manager.
    """

    class context_manager:
        """
        Context manager for initializing, creating, obtaining output from, and destroying a Terraform resource.
        """

        def __init__(self, context):
            self._context = context
            self._output = None

        def __enter__(self):
            if init:
                init(self._context)
            if apply:
                apply(self._context)

            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if destroy:
                destroy(self._context)

        @property
        def output(self):
            if self._output is None:
                self._output = output(self._context)

            return self._output

    return context_manager
