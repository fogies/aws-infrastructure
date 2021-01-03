from invoke import task
import json


class ConfigurationEncoder(json.JSONEncoder):
    """
    Simple encoder
    """

    def default(self, obj):
        # Use of __str__ has been sufficient
        # Otherwise would detect specific objects and return encodings

        return str(obj)


def template_config():
    """
    Template for a task to print the task configuration.
    """

    @task
    def config(context):
        """
        Print the task configuration.
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

        # Spacing between sections
        print()

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

    return config
