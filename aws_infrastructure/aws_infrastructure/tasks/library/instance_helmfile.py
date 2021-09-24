from invoke import task
from pathlib import Path
import ruamel.yaml
from typing import Union

import aws_infrastructure.tasks.library.instance_ssh


def _helmfile_apply(
    *,
    ssh_config: aws_infrastructure.tasks.library.instance_ssh.SSHConfig,
    dir_staging_local: Path,
    dir_staging_remote: Path,
    path_helmfile: Path,
    helmfile_config,
    path_helmfile_config_base: Path,
):
    # Connect via SSH
    with aws_infrastructure.tasks.library.instance_ssh.SSHClientContextManager(ssh_config=ssh_config) as ssh_client:
        # Create a staging directory
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
                        path_helmfile_config_base,
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
    ssh_config: aws_infrastructure.tasks.library.instance_ssh.SSHConfig,
    dir_staging_local: Union[Path, str],
    dir_staging_remote: Union[Path, str],
):
    @task
    def helmfile_apply(context, helmfile):
        """
        Apply a helmfile in the instance.
        """
        print('Applying helmfile')

        dir_staging_local = Path(dir_staging_local)
        dir_staging_remote = Path(dir_staging_remote)

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
        elif Path(helmfile).suffix.casefold() == '.yaml':
            path_helmfile_config = None
            path_helmfile = Path(helmfile)
        else:
            print('No matching helmfile-config.yaml or helmfile found.')
            return

        if path_helmfile_config:
            # Print the specific configuration we will use
            print('Found matching helmfile-config.yaml at: {}'.format(path_helmfile_config))

            # Load the config
            with open(path_helmfile_config) as file_config:
                loaded_helmfile_config = ruamel.yaml.safe_load(file_config)

            # Obtain the helmfile from the configuration
            path_helmfile = Path(
                path_helmfile_config.parent,
                loaded_helmfile_config['helmfile']
            )
            # Config paths are relative to the config
            path_helmfile_config_base = path_helmfile_config.parent
        elif path_helmfile and path_helmfile.is_file():
            # Print the specific helmfile we will use
            print('Found matching helmfile at: {}'.format(path_helmfile))

            # No valid config
            loaded_helmfile_config = {}
            path_helmfile_config_base = None
        else:
            print('No matching helmfile at: {}'.format(path_helmfile))
            return

        _helmfile_apply(
            ssh_config=ssh_config,
            dir_staging_local=dir_staging_local,
            dir_staging_remote=dir_staging_remote,
            path_helmfile=path_helmfile,
            helmfile_config=loaded_helmfile_config,
            path_helmfile_config_base=path_helmfile_config_base,
        )

    return helmfile_apply
