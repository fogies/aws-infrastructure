import json

from invoke import Collection
from invoke import task


class ConfigurationEncoder(json.JSONEncoder):
    """
    Simple encoder for displaying Invoke configuration.
    """

    def default(self, obj):
        # Use of __str__ has been sufficient
        # Otherwise would detect specific objects and return encodings

        return str(obj)


def task_display():
    """
    Create a task to display the Invoke configuration.
    """

    @task
    def display(context):
        """
        Display the Invoke configuration.
        """

        # Split out Invoke's default configuration fields
        keys_internal = [
            'run',
            'runners',
            'sudo',
            'tasks',
            'timeouts',
        ]

        config_internal = {
            key: value for (key, value) in context.config.items() if key in keys_internal
        }
        config_tasks = {
            key: value for (key, value) in context.config.items() if key not in keys_internal
        }

        # Print task configuration
        print('==================')
        print('Task Configuration')
        print('==================')
        print(
            json.dumps(
                config_tasks,
                cls=ConfigurationEncoder,
                indent=4,
                sort_keys=True,
            )
        )

        # Spacing between sections
        print()

        # Print internal configuration
        print('====================')
        print('Invoke Configuration')
        print('====================')
        print(
            json.dumps(
                config_internal,
                cls=ConfigurationEncoder,
                indent=4,
                sort_keys=True,
            )
        )

    return display


def create_tasks(
    # *,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    ns = Collection('config')

    display = task_display()
    ns.add_task(display)

    return ns
