from invoke import Collection
from invoke import task
import io
import os
import paramiko
from pathlib import Path
import re
import ruamel.yaml
import select
import semver
import socketserver
from typing import List
from typing import Union


class SSHClientContextManager:
    """
    Context manager for connecting, using, and destroying an SSH client.
    """
    def __init__(self, *, instance_config):
        self._instance_config = instance_config
        self._client = None

    def __enter__(self):
        self._ssh_connect()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ssh_destroy()

    @property
    def client(self):
        """
        The SSH client.
        """
        return self._client

    def exec_command(self, *, command: Union[str, List[str]]):
        """
        Execute a command, print the command with its stdout and stderr.
        """

        print('Command')
        if isinstance(command, str):
            # Single commands are just printed and passed through
            print('  ' + command)
        elif isinstance(command, List):
            # Multiple commands are printed, then reformatted into a single command

            for command_current in command:
                print('  ' + command_current)

            command = '\n'.join(command)
        else:
            raise ValueError

        stdin, stdout, stderr = self.client.exec_command(
            command=command
        )

        line = stdout.readline()
        if line:
            print('Output')
            while line:
                print('  ' + line.rstrip())
                line = stdout.readline()

        line = stderr.readline()
        if line:
            print('Error')
            while line:
                print('  ' + line.rstrip())
                line = stderr.readline()

    def _ssh_connect(self):
        """
        Connect an SSH client to the instance.
        """
        class IgnorePolicy(paramiko.MissingHostKeyPolicy):
            """
            Policy for ignoring missing host keys.

            TODO: It would be better to know and confirm the host key.
            """

            def missing_host_key(self, client, hostname, key):
                return

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(IgnorePolicy())
        client.connect(
            hostname=self._instance_config['instance_ip'],
            username=self._instance_config['instance_user'],
            pkey=paramiko.rsakey.RSAKey.from_private_key(io.StringIO(self._instance_config['instance_key']))
        )

        self._client = client

    def _ssh_destroy(self):
        """
        Destroy an SSH client that is connected to the instance.
        """
        self._client.close()
        self._client = None


class SFTPClientContextManager:
    """
    Context manager for connecting, using, and destroying an SFTP client.
    """
    def __init__(self, *, ssh_client):
        self._ssh_client = ssh_client
        self._client = None

    def __enter__(self):
        self._sftp_connect()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._sftp_destroy()

    @property
    def client(self):
        """
        The SFTP client.
        """
        return self._client

    def _sftp_connect(self):
        """
        Obtain an SFTP client to the instance.
        """
        self._client = self._ssh_client.client.open_sftp()

    def _sftp_destroy(self):
        """
        Destroy an SSH client that is connected to the instance.
        """
        self._client.close()
        self._client = None


class PortForwardContextManager:
    """
    Context manager for forwarding a port through an ssh client.
    """
    def __init__(self, *, ssh_client, local_port, remote_port):
        self._ssh_client = ssh_client
        self._local_port = local_port
        self._remote_port = remote_port
        self._server = None

    def __enter__(self):
        self._port_forward_start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._port_forward_destroy()

    def _create_handler(self, ssh_client, remote_port):
        class Handler(socketserver.BaseRequestHandler):
            _ssh_client = ssh_client
            _remote_port = remote_port

            def handle(self):
                channel = self._ssh_client.get_transport().open_channel(
                    kind='direct-tcpip',
                    dest_addr=('localhost', remote_port),
                    src_addr=self.request.getpeername(),
                )

                while True:
                    # If either direction has data available, forward that data
                    r, w, x = select.select([self.request, channel], [], [])
                    if self.request in r:
                        data = self.request.recv(1024 * 1024)
                        if len(data) == 0:
                            break
                        channel.send(data)
                        print('{} bytes sent'.format(len(data)))
                    if channel in r:
                        data = channel.recv(1024 * 1024)
                        if len(data) == 0:
                            break
                        self.request.send(data)
                        print('{} bytes received'.format(len(data)))

                channel.close()
                self.request.close()

        return Handler

    def forward_forever(self):
        """
        Handle incoming requests forever.
        """
        self._server.serve_forever()

    def _port_forward_start(self):
        """
        Start the port forwarding server.
        """
        self._server = socketserver.ThreadingTCPServer(
            server_address=('localhost', self._local_port),
            RequestHandlerClass=self._create_handler(self._ssh_client.client, self._remote_port),
        )

        print('Forwarding local port {} to remote port {}'.format(self._local_port, self._remote_port))

    def _port_forward_destroy(self):
        """
        Stop the port forwarding server.

        In practice it will already be stopped, as this code is only reached by a keyboard interrupt.
        """
        self._server.shutdown()
        self._server = None


def _task_ssh(
    *,
    config_key: str,
    dir_terraform: Path,
    instance_config
):
    """
    Create a task to open an SSH session to the instance.
    """

    @task
    def ssh(context):
        """
        Open an SSH session to the instance.
        """
        print('Creating SSH session')

        dir_instance = Path(dir_terraform, instance_config['instance_name'])

        # Launch an external SSH session,
        # which seems more appropriate than attempting via Paramiko.
        context.run(
            command=' '.join([
                'start',  # Ensures Windows launches ssh outside cmd
                          # This has been only way to obtain a proper terminal
                'ssh',
                '-l {}'.format(instance_config['instance_user']),
                '-i {}'.format(Path(dir_instance, instance_config['instance_key_file'])),
                '-o StrictHostKeyChecking=no',
                '-o UserKnownHostsFile="{}"'.format(Path(dir_instance, 'known_hosts')),
                instance_config['instance_ip']
            ]),
            disown=True
        )

    return ssh


def _task_ssh_port_forward(
    *,
    config_key: str,
    instance_config
):
    """
    Create a task to forward a port from the instance.
    """

    @task
    def ssh_port_forward(context, port, local_port=None):
        """
        Forward a port from the instance.
        """

        # Map our parameters to a remote and local port
        remote_port = int(port)
        if local_port:
            local_port = int(local_port)
        else:
            local_port = remote_port

        # Connect via SSH
        with SSHClientContextManager(instance_config=instance_config) as ssh_client:
            # Initiate port forwarding
            with PortForwardContextManager(
                ssh_client=ssh_client,
                local_port=local_port,
                remote_port=remote_port
            ) as port_forward:
                port_forward.forward_forever()

    return ssh_port_forward


def _task_docker_build(
    *,
    config_key: str,
    instance_config
):
    @task
    def docker_build(context, docker_config):
        """
        Build a Docker image.
        """
        print('Building Docker image')

        # docker_config must be a path to a file named docker-config.yaml
        if not (Path(docker_config).is_file() and Path(docker_config).name == 'docker-config.yaml'):
            print('No matching docker-config.yaml found.')
            return

        # Print the specific configuration we will use
        print('Found matching docker-config.yaml at: {}'.format(docker_config))

        # Load the config
        with open(docker_config) as file_config:
            loaded_config = ruamel.yaml.safe_load(file_config)

        # Connect via SSH
        with SSHClientContextManager(instance_config=instance_config) as ssh_client:
            # Create a staging directory
            ssh_client.exec_command(command=[
                'rm -rf .minikube_helm_staging',
                'mkdir -p .minikube_helm_staging'
            ])

            # Upload the Dockerfile.
            #
            # The configuration 'dockerfile' is a path relative to the location of the docker-config.
            dockerfile = Path(
                Path(docker_config).parent,
                loaded_config['dockerfile']
            )
            with SFTPClientContextManager(ssh_client=ssh_client) as sftp_client:
                sftp_client.client.chdir('.minikube_helm_staging')
                sftp_client.client.put(
                    localpath=str(dockerfile),
                    remotepath='Dockerfile',
                )

            ssh_client.exec_command(command=[
                # Point the session Docker CLI at our Minikube Docker context
                'eval $(minikube -p minikube docker-env)',
                'cd .minikube_helm_staging',
                ' '.join([
                    'docker',
                    'build',
                    # Until we have a strategy for cache busting, always use no-cache
                    '--no-cache',
                    # Until we have a strategy for CPU usage, limit to 50%
                    '--cpu-period=100000 --cpu-quota=50000',
                    # List of build-arg parameters
                    ' '.join([
                        '--build-arg "{}={}"'.format(key_current, value_current)
                        for (key_current, value_current)
                        in loaded_config['args'].items()
                    ]),
                    # List of tag parameters
                    ' '.join([
                        '--tag "{}"'.format(tag_current)
                        for tag_current
                        in loaded_config['tags']
                    ]),
                    '.'
                ])
            ])

            # Remove the staging directory
            ssh_client.exec_command(command='rm -rf .minikube_helm_staging')

    return docker_build


def _task_helm_install(
    *,
    config_key: str,
    dir_helm_repo: Path,
    instance_config
):
    @task
    def helm_install(context, helm_chart):
        """
        Install a chart in the instance.
        """
        print('Installing chart')

        # helm_chart might be:
        # - a full path (e.g., 'helm_repo/ingress-0.1.0.tgz')
        # - a file (e.g., 'ingress-0.1.0.tgz')
        # - a name including a version (e.g., 'ingress-0.1.0')
        # - a name absent a version (e.g., 'ingress')
        #
        # Convert it to a full path before further use.
        if len(Path(helm_chart).parts) > 1:
            # A full path (e.g., 'helm_repo/ingress-0.1.0.tgz').
            # Use it as a complete path to a chart.
            helm_chart = Path(helm_chart)
        elif (match := re.match('(.+)-([0-9\\.]+)\\.tgz', helm_chart)) is not None:
            # A file (e.g., 'ingress-0.1.0.tgz').
            # Use it to reference a file in helm_charts_dir.
            helm_chart = Path(dir_helm_repo, helm_chart)
        elif (match := re.match('(.+)-([0-9\\.]+)', helm_chart)) is not None:
            # A name including a version (e.g., 'ingress-0.1.0').
            # Use it to reference a file in helm_charts_dir.
            helm_chart = Path(dir_helm_repo, '{}.tgz'.format(helm_chart))
        else:
            # A name absent a version (e.g., 'ingress').
            # Find the latest matching chart in helm_charts_dir.
            # Current implemented by looking directly at the files in the repo.
            # Alternatively, could parse and examine `index.yaml`.
            helm_chart_latest = None
            helm_chart_version_latest = None
            for root, dirs, files in os.walk(dir_helm_repo):
                for file_current in files:
                    if (match := re.match('(.+)-([0-9\\.]+)\\.tgz', file_current)) is not None:
                        match_chart = match.group(1)
                        match_version = semver.VersionInfo.parse(match.group(2))
                        if match_chart == helm_chart:
                            if (helm_chart_version_latest is None) or (match_version > helm_chart_version_latest):
                                helm_chart_latest = Path(root, file_current)
                                helm_chart_version_latest = match_version

            if helm_chart_latest:
                helm_chart = helm_chart_latest

        # Ensure we now have a path to a specific chart
        if not Path(helm_chart).is_file():
            print('No matching chart found.')
            return

        # Print the specific chart we will use
        print('Found matching chart at: {}'.format(helm_chart))

        # Will need chart file name separate from its path
        helm_chart_file_name = Path(helm_chart).name

        # Will need chart name separate from its version
        match = re.match('(.+)-(.+)\\.tgz', Path(helm_chart).name)
        helm_chart_name = match.group(1)

        # Connect via SSH
        with SSHClientContextManager(instance_config=instance_config) as ssh_client:
            # Create a staging directory
            ssh_client.exec_command(command=[
                'rm -rf .minikube_helm_staging',
                'mkdir -p .minikube_helm_staging'
            ])

            # Upload the chart file
            with SFTPClientContextManager(ssh_client=ssh_client) as sftp_client:
                sftp_client.client.chdir('.minikube_helm_staging')
                sftp_client.client.put(
                    localpath=Path(helm_chart),
                    remotepath=helm_chart_file_name,
                )

            # Install the chart.
            # Skip CRDs to require pattern of installing them separately.
            ssh_client.exec_command(command=' '.join([
                'helm',
                'upgrade',
                '--install',
                '--skip-crds',
                helm_chart_name,
                '.minikube_helm_staging/{}'.format(helm_chart_file_name)
            ]))

            # Remove the staging directory
            ssh_client.exec_command(command='rm -rf .minikube_helm_staging')

    return helm_install


def _task_helmfile_apply(
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


def _task_ip(
    *,
    config_key: str,
    instance_config
):
    @task
    def ip(context):
        """
        Print the public IP of the instance.
        """
        print(instance_config['instance_ip'])

    return ip


def create_tasks(
    *,
    config_key: str,
    dir_terraform: Union[Path, str],
    dir_helm_repo: Union[Path, str],
    instance: str,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    dir_terraform = Path(dir_terraform)
    dir_helm_repo = Path(dir_helm_repo)

    with open(Path(dir_terraform, instance, 'config.yaml')) as file_config:
        yaml_config = ruamel.yaml.safe_load(file_config)

    instance_name = yaml_config['instance_name']

    ns = Collection(instance_name)

    ssh = _task_ssh(
        config_key=config_key,
        dir_terraform=dir_terraform,
        instance_config=yaml_config
    )
    ns.add_task(ssh)

    ssh_port_forward = _task_ssh_port_forward(
        config_key=config_key,
        instance_config=yaml_config
    )
    ns.add_task(ssh_port_forward)

    docker_build = _task_docker_build(
        config_key=config_key,
        instance_config=yaml_config
    )
    ns.add_task(docker_build)

    helm_install = _task_helm_install(
        config_key=config_key,
        dir_helm_repo=dir_helm_repo,
        instance_config=yaml_config
    )
    ns.add_task(helm_install)

    helmfile_apply = _task_helmfile_apply(
        config_key=config_key,
        instance_config=yaml_config
    )
    ns.add_task(helmfile_apply)

    ip = _task_ip(
        config_key=config_key,
        instance_config=yaml_config
    )
    ns.add_task(ip)

    return ns
