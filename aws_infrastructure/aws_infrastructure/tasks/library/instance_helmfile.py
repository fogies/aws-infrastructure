from invoke import task
import os.path
from pathlib import Path
import ruamel.yaml
from typing import Union

import aws_infrastructure.tasks.ssh

def _helmfile_apply(
    *,
    context,
    ssh_config_path: Path,
    staging_local_dir: Path,
    staging_remote_dir: Path,
    helmfile_path: Path,
    helmfile_config_path: Path,
    helmfile_values_factories = None, # Dictionary from string to function that returns dictionary
):
    # Load any config
    helmfile_config = {}
    if helmfile_config_path is not None:
        with open(helmfile_config_path) as file_config:
            helmfile_config = ruamel.yaml.safe_load(file_config)

    # If we have values_variables, process them
    if helmfile_values_factories:
        # Create a local 'values' staging directory
        dir_staging_values_local = Path(staging_local_dir, 'values')
        dir_staging_values_local.mkdir(parents=True, exist_ok=True)

        # Process each values_variable
        for values_name_current, values_factory_current in helmfile_values_factories.items():
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
                'file': os.path.relpath(path_staging_values_local_current, helmfile_config_path.parent),
                'destination': path_staging_values_remote_current,
            })

    # Connect via SSH
    ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(ssh_config_path=ssh_config_path)
    with aws_infrastructure.tasks.ssh.SSHClientContextManager(ssh_config=ssh_config) as ssh_client:
        # Create a remote staging directory
        ssh_client.exec_command(command=[
            'rm -rf {}'.format(staging_remote_dir.as_posix()),
            'mkdir -p {}'.format(staging_remote_dir.as_posix()),
        ])

        with aws_infrastructure.tasks.ssh.SFTPClientContextManager(ssh_client=ssh_client) as sftp_client:
            # FTP within the staging directory
            sftp_client.paramiko_sftp_client.chdir(staging_remote_dir.as_posix())

            # Upload any dependencies in any provided configuration
            for dependency_current in helmfile_config.get('dependencies', []):
                if 'file' in dependency_current:
                    # Process a file dependency
                    path_local = Path(
                        helmfile_config_path.parent,
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
                                    staging_remote_dir,
                                    path_remote.parent
                                ).as_posix()
                            )
                        ])

                    # Upload the dependency file
                    sftp_client.paramiko_sftp_client.put(
                        localpath=str(path_local),
                        remotepath=str(path_remote.as_posix()),
                    )
                else:
                    print('Unknown dependency type: {}'.format(dependency_current))
                    return

            # Upload the helmfile
            print('Uploading helmfile at: {}'.format(helmfile_path))
            sftp_client.paramiko_sftp_client.put(
                localpath=helmfile_path,
                remotepath=helmfile_path.name,
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
                    staging_remote_dir,
                    helmfile_path.name
                ).as_posix()
            ),
            'apply',
            '--skip-diff-on-install',
        ]))

        # Remove the staging directory
        ssh_client.exec_command(command='rm -rf {}'.format(staging_remote_dir.as_posix()))


def task_helmfile_apply(
    *,
    config_key: str,
    ssh_config_path: Union[Path, str],
    staging_local_dir: Union[Path, str],
    staging_remote_dir: Union[Path, str],
    helmfile_path: Union[Path, str],
    helmfile_config_path: Union[Path, str],
    helmfile_values_factories, # Dictionary from string to function that returns dictionary
):
    """
    Create a task for applying a specified helmfile with any necessary values_variables.
    """

    ssh_config_path = Path(ssh_config_path)
    staging_local_dir = Path(staging_local_dir)
    staging_remote_dir = Path(staging_remote_dir)
    helmfile_path = Path(helmfile_path)
    helmfile_config_path = Path(helmfile_config_path)

    @task
    def helmfile_apply(context):
        """
        Apply a helmfile in the instance.
        """
        print('Applying helmfile')

        _helmfile_apply(
            context=context,
            ssh_config_path=ssh_config_path,
            staging_local_dir=staging_local_dir,
            staging_remote_dir=staging_remote_dir,
            helmfile_path=helmfile_path,
            helmfile_config_path=helmfile_config_path,
            helmfile_values_factories=helmfile_values_factories,
        )

    return helmfile_apply


def task_helmfile_apply_generic(
    *,
    config_key: str,
    ssh_config_path: Union[Path, str],
    staging_local_dir: Union[Path, str],
    staging_remote_dir: Union[Path, str],
):
    """
    Create a generic task for applying a helmfile specified on the command line.

    A generic task does not support values_variables.
    """

    ssh_config_path = Path(ssh_config_path)
    staging_local_dir = Path(staging_local_dir)
    staging_remote_dir = Path(staging_remote_dir)

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
            helmfile_config_path = Path(helmfile)
            helmfile_path = None
        elif Path(helmfile).is_dir() and Path(helmfile, 'helmfile-config.yaml').is_file():
            helmfile_config_path = Path(helmfile, 'helmfile-config.yaml')
            helmfile_path = None
        elif Path(helmfile).is_dir() and Path(helmfile, 'helmfile.yaml').is_file():
            helmfile_config_path = None
            helmfile_path = Path(helmfile, 'helmfile.yaml')
        elif Path(helmfile).suffix.casefold() == '.yaml' and Path(helmfile).is_file():
            helmfile_config_path = None
            helmfile_path = Path(helmfile)
        else:
            print('No matching helmfile-config.yaml or helmfile found.')
            return

        if helmfile_config_path and helmfile_config_path.is_file():
            # Print the specific configuration we will use
            print('Found matching helmfile-config.yaml at: {}'.format(helmfile_config_path))

            # Load the config
            with open(helmfile_config_path) as file_config:
                helmfile_config = ruamel.yaml.safe_load(file_config)

            # Obtain the helmfile from the configuration
            helmfile_path = Path(
                helmfile_config_path.parent,
                helmfile_config['helmfile']
            )

        if helmfile_path and helmfile_path.is_file():
            # Print the specific helmfile we will use
            print('Found matching helmfile at: {}'.format(helmfile_path))
        else:
            print('No matching helmfile at: {}'.format(helmfile_path))
            return

        _helmfile_apply(
            context=context,
            ssh_config_path=ssh_config_path,
            staging_local_dir=staging_local_dir,
            staging_remote_dir=staging_remote_dir,
            helmfile_path=helmfile_path,
            helmfile_config_path=helmfile_config_path,
        )

    return helmfile_apply
