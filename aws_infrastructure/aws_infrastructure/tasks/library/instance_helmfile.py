from invoke import task
import os.path
from pathlib import Path
import ruamel.yaml
from typing import Union

import aws_infrastructure.tasks.library.instance_ssh

DIR_STAGING_REMOTE_HELMFILE = './.staging/helmfile'

def _helmfile_apply(
    *,
    context,
    path_ssh_config: Path,
    dir_staging_local: Path,
    dir_staging_remote: Path,
    path_helmfile: Path,
    path_helmfile_config: Path,
    values_variables = None, # Dictionary from string to function that returns dictionary
):
    # Default remote staging directory
    if dir_staging_remote is None:
        dir_staging_remote = Path(DIR_STAGING_REMOTE_HELMFILE)

    # Load any config
    if path_helmfile_config is not None:
        with open(path_helmfile_config) as file_config:
            helmfile_config = ruamel.yaml.safe_load(file_config)
    else:
        helmfile_confg = {}

    # If we have values_variables, process them
    if values_variables:
        # Create a local 'values' staging directory
        dir_staging_values_local = Path(dir_staging_local, 'values')
        dir_staging_values_local.mkdir(parents=True, exist_ok=True)

        # Process each values_variable
        for values_name_current, values_factory_current in values_variables.items():
            # Obtain the values from the factory
            values_current = values_factory_current(context=context)

            # Store the values in local staging
            path_staging_values_local_current = Path(dir_staging_values_local, '{}.values.yaml'.format(values_name_current))
            with open(path_staging_values_local_current, 'w') as file_values_current:
                yaml = ruamel.yaml.YAML()
                yaml.dump(values_current, file_values_current)

            # Upload with a path relative to the config
            path_staging_values_remote_current = Path('values', '{}.values.yaml'.format(values_name_current))

            # Update the configuration to include the upload
            if 'dependencies' not in helmfile_config:
                helmfile_config['dependencies'] = []

            # Local file path will be interpeted relative to the directory containing the helmfile_config
            helmfile_config['dependencies'].append({
                'file': os.path.relpath(path_staging_values_local_current, path_helmfile_config.parent),
                'destination': path_staging_values_remote_current,
            })

    # Connect via SSH
    ssh_config = aws_infrastructure.tasks.library.instance_ssh.SSHConfig(path_ssh_config=path_ssh_config)
    with aws_infrastructure.tasks.library.instance_ssh.SSHClientContextManager(ssh_config=ssh_config) as ssh_client:
        # Create a remote staging directory
        ssh_client.exec_command(command=[
            'rm -rf {}'.format(dir_staging_remote.as_posix()),
            'mkdir -p {}'.format(dir_staging_remote.as_posix()),
        ])

        with aws_infrastructure.tasks.library.instance_ssh.SFTPClientContextManager(ssh_client=ssh_client) as sftp_client:
            # FTP within the staging directory
            sftp_client.client.chdir(dir_staging_remote.as_posix())

            # Upload any dependencies in any provided configuration
            for dependency_current in helmfile_config.get('dependencies', []):
                if 'file' in dependency_current:
                    # Process a file dependency
                    path_local = Path(
                        path_helmfile_config.parent,
                        dependency_current['file']
                    )
                    path_remote = Path(
                        dependency_current['destination']
                    )

                    # Ensure the dependency exists
                    if not path_local.is_file():
                        print('Dependency not found at: {}'.format(path_local))
                        return

                    # Ensure any remote directories exist
                    if path_remote.parent != Path('.'):
                        ssh_client.exec_command(command=[
                            'mkdir -p {}'.format(
                                Path(
                                    dir_staging_remote,
                                    path_remote.parent
                                ).as_posix()
                            )
                        ])

                    # Upload the dependency file
                    sftp_client.client.put(
                        localpath=str(path_local),
                        remotepath=str(path_remote.as_posix()),
                    )
                else:
                    print('Unknown dependency type: {}'.format(dependency_current))
                    return

            # Upload the helmfile
            print('Uploading helmfile at: {}'.format(path_helmfile))
            sftp_client.client.put(
                localpath=path_helmfile,
                remotepath=path_helmfile.name,
            )

        # Apply the helmfile
        #
        # Use --skip-diff-on-install because:
        # - Missing CRDs will cause helm diff to fail
        # - helm diff output tends to be large for a new install
        ssh_client.exec_command(command=' '.join([
            'helmfile',
            '--file {}'.format(
                Path(
                    dir_staging_remote,
                    path_helmfile.name
                ).as_posix()
            ),
            'apply',
            '--skip-diff-on-install',
        ]))

        # Remove the staging directory
        ssh_client.exec_command(command='rm -rf {}'.format(dir_staging_remote.as_posix()))


def task_helmfile_apply(
    *,
    config_key: str,
    path_ssh_config: Union[Path, str],
    dir_staging_local: Union[Path, str],
    dir_staging_remote: Union[Path, str] = None,
    path_helmfile: Union[Path, str],
    path_helmfile_config: Union[Path, str],
    values_variables, # Dictionary from string to function that returns dictionary
):
    """
    Create a task for applying a specified helmfile with any necessary values_variables.
    """

    path_ssh_config = Path(path_ssh_config)
    dir_staging_local = Path(dir_staging_local)
    if dir_staging_remote is not None:
        dir_staging_remote = Path(dir_staging_remote)
    path_helmfile = Path(path_helmfile)
    path_helmfile_config = Path(path_helmfile_config)

    @task
    def helmfile_apply(context):
        """
        Apply a helmfile in the instance.
        """
        print('Applying helmfile')

        _helmfile_apply(
            context=context,
            path_ssh_config=path_ssh_config,
            dir_staging_local=dir_staging_local,
            dir_staging_remote=dir_staging_remote,
            path_helmfile=path_helmfile,
            path_helmfile_config=path_helmfile_config,
            values_variables=values_variables,
        )

    return helmfile_apply


def task_helmfile_apply_generic(
    *,
    config_key: str,
    path_ssh_config: Union[Path, str],
    dir_staging_local: Union[Path, str],
    dir_staging_remote: Union[Path, str] = None,
):
    """
    Create a generic task for applying a helmfile specified on the command line.

    A generic task does not support values_variables.
    """

    path_ssh_config = Path(path_ssh_config)
    dir_staging_local = Path(dir_staging_local)
    if dir_staging_remote is not None:
        dir_staging_remote = Path(dir_staging_remote)

    @task
    def helmfile_apply(context, helmfile):
        """
        Apply a helmfile in the instance.
        """
        print('Applying helmfile')

        # helmfile might be:
        # - a path to a 'helmfile-config.yaml', in which case process the config
        # - a path to a directory that contains a 'helmfile-config.yaml', in which case process the config
        # - a path to a directory that contains a 'helmfile.yaml', in which cased process as a helmfile
        # - a path to any other file with a '.yaml' extension, in which case attempt to process as a helmfile

        if Path(helmfile).is_file() and Path(helmfile).name == 'helmfile-config.yaml':
            path_helmfile_config = Path(helmfile)
            path_helmfile = None
        elif Path(helmfile).is_dir() and Path(helmfile, 'helmfile-config.yaml').is_file():
            path_helmfile_config = Path(helmfile, 'helmfile-config.yaml')
            path_helmfile = None
        elif Path(helmfile).is_dir() and Path(helmfile, 'helmfile.yaml').is_file():
            path_helmfile_config = None
            path_helmfile = Path(helmfile, 'helmfile.yaml')
        elif Path(helmfile).suffix.casefold() == '.yaml' and Path(helmfile).is_file():
            path_helmfile_config = None
            path_helmfile = Path(helmfile)
        else:
            print('No matching helmfile-config.yaml or helmfile found.')
            return

        if path_helmfile_config and path_helmfile_config.is_file():
            # Print the specific configuration we will use
            print('Found matching helmfile-config.yaml at: {}'.format(path_helmfile_config))

            # Load the config
            with open(path_helmfile_config) as file_config:
                helmfile_config = ruamel.yaml.safe_load(file_config)

            # Obtain the helmfile from the configuration
            path_helmfile = Path(
                path_helmfile_config.parent,
                helmfile_config['helmfile']
            )

        if path_helmfile and path_helmfile.is_file():
            # Print the specific helmfile we will use
            print('Found matching helmfile at: {}'.format(path_helmfile))
        else:
            print('No matching helmfile at: {}'.format(path_helmfile))
            return

        _helmfile_apply(
            context=context,
            path_ssh_config=path_ssh_config,
            dir_staging_local=dir_staging_local,
            dir_staging_remote=dir_staging_remote,
            path_helmfile=path_helmfile,
            path_helmfile_config=path_helmfile_config,
        )

    return helmfile_apply
