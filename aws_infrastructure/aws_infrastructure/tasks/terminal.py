"""
Helper for invoking tasks in new terminals.
"""

from invoke.context import Context
import os
from pathlib import Path
import platform
import stat
import sys


def _format_export(name: str, value: str) -> str:
    """
    Format a command to export an environment variable.
    """

    return 'export {}="{}"'.format(name, value)


def spawn_new_terminal(
    context: Context,
) -> bool:
    """
    Spawn a new terminal to run the current command.

    Returns True in the new terminal, False in the original terminal.

    Currently implemented using an environment variable to flag being in a new terminal.
    This implementation likely does not allow spawned terminals to further spawn additional terminals.
    """

    # Detect if we are already in a new terminal, return immediately
    if os.getenv('INVOKE_SPAWN_NEW_TERMINAL'):
        return True

    # Reconstruct the command line
    command = "invoke"
    for arg_current in sys.argv[1:]:
        command = '{} "{}"'.format(command, arg_current)

    # According to platform, prepare to execute the command
    platform_current = platform.system()

    if platform_current.casefold() == 'windows':
        # On Windows:
        # - Use `start` to open a new window.
        # - Use the `cmd` terminal.
        # - Provide `/k` to keep the `cmd` terminal open upon completion (e.g., to view output when debugging).
        #
        # The new terminal will start in the same directory with the same environment variables.

        # Construct the command we actually execute
        command = 'start cmd /k {}'.format(command)

        # Spawn the new terminal
        context.run(
            command=command,
            # Set the INVOKE_SPAWN_NEW_TERMINAL environment variable we will detect from the new terminal
            env={
                'INVOKE_SPAWN_NEW_TERMINAL': 'True'
            },
            # Asynchronously allow the task to proceed in the new terminal
            disown=True
        )
    elif platform_current.casefold() == 'darwin':
        # On Mac:
        # - Write out a command file.
        # - Make that file executable.
        # - `open` it via a new `Terminal`
        #
        # The new terminal will start in the person's home directory and does not inherit environment variables.

        path_cwd = Path.cwd()
        path_command = Path(path_cwd, 'INVOKE_SPAWN_NEW_TERMINAL.command')
        with open(path_command, 'w') as file_command:
            # Write a command file
            file_command.writelines('{}\n'.format(line_current) for line_current in [
                '# Set environment variable that we will detect from the new terminal',
                _format_export('INVOKE_SPAWN_NEW_TERMINAL', 'True'),
                '',
                '# Restore the working directory',
                'cd "{}"'.format(path_cwd),
                '',
                '# Restore environment variables that configure the virtual environment',
                '# Based on a manual inspection of relevant variables on 7/13/2021, perhaps this could be done better',
                _format_export('PATH', os.getenv('PATH')),
                _format_export('PIPENV_ACTIVE', os.getenv('PIPENV_ACTIVE')),
                _format_export('PIP_DISABLE_PIP_VERSION_CHECK', os.getenv('PIP_DISABLE_PIP_VERSION_CHECK')),
                _format_export('PIP_PYTHON_PATH', os.getenv('PIP_PYTHON_PATH')),
                _format_export('PS1', os.getenv('PS1')),
                _format_export('PYTHONDONTWRITEBYTECODE', os.getenv('PYTHONDONTWRITEBYTECODE')),
                _format_export('VIRTUAL_ENV', os.getenv('VIRTUAL_ENV')),
                '',
                '# Delete this command file',
                'rm -f "{}"'.format(path_command),
                '',
                '# Finally, invoke the command in the new terminal',
                '{}'.format(command),
            ])

            # Make the command file executable
            path_command.chmod(path_command.stat().st_mode | stat.S_IXUSR)

            # Construct the command we actually execute
            command = 'open -a Terminal "{}"'.format(path_command)

            # Spawn the new terminal
            context.run(
                command=command,
                # Asynchronously allow the task to proceed in the new terminal
                disown=True
            )
    else:
        raise ValueError('Unsupported platform in spawn_new_terminal: "{}"'.format(platform_current))

    return False
