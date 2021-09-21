from invoke import task
from pathlib import Path

import aws_infrastructure.tasks.library.instance_ssh

def task_helmfile_apply(
    *,
    config_key: str,
    instance_config
):
    @task
    def helmfile_apply(context, helmfile):
        """
        Apply a helmfile in the instance.
        """
        print('Applying helmfile')

        # task_config = context.config[config_key]
        # working_dir = Path(task_config.working_dir)

        # helmfile might be:
        # - a path to a 'helmfile-config.yaml', in which case process the config
        # - a path to a directory that contains a 'helmfile-config.yaml', in which case process the config
        # - a path to any other file with a '.yaml' extension, in which case attempt to process as a helmfile

        if Path(helmfile).is_file() and Path(helmfile).name == 'helmfile-config.yaml':
            path_helmfile_config = Path(helmfile)
            path_helmfile = None
        elif Path(helmfile).is_dir() and Path(helmfile, 'helmfile-config.yaml').is_file():
            path_helmfile_config = Path(helmfile, 'helmfile-config.yaml')
            path_helmfile = None
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
                loaded_config = ruamel.yaml.safe_load(file_config)

            # Obtain the helmfile from the configuration
            path_helmfile = Path(
                path_helmfile_config.parent,
                loaded_config['helmfile']
            )

        if path_helmfile:
            if path_helmfile.is_file():
                # Print the specific helmfile we will use
                print('Found matching helmfile at: {}'.format(path_helmfile))
            else:
                print('No matching helmfile at: {}'.format(path_helmfile))
                return

        # Connect via SSH
        with SSHClientContextManager(instance_config=instance_config) as ssh_client:
            path_staging = Path('.minikube_helm_staging')

            # Create a staging directory
            ssh_client.exec_command(command=[
                'rm -rf {}'.format(path_staging.as_posix()),
                'mkdir -p {}'.format(path_staging.as_posix()),
            ])

            with SFTPClientContextManager(ssh_client=ssh_client) as sftp_client:
                # FTP within the staging directory
                sftp_client.client.chdir(str(path_staging))

                # Upload any dependencies in any provided configuration
                if path_helmfile_config and 'dependencies' in loaded_config:
                    for dependency_current in loaded_config['dependencies']:
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
                                            path_staging,
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
                    localpath=str(Path(path_helmfile)),
                    remotepath=str(Path(path_helmfile).name),
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
                        path_staging,
                        path_helmfile.name
                    ).as_posix()
                ),
                'apply',
                '--skip-diff-on-install',
            ]))

            # Remove the staging directory
            ssh_client.exec_command(command='rm -rf .minikube_helm_staging')

    return helmfile_apply
