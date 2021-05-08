import io
import os
import re
from typing import List
from typing import Union

from invoke import Collection
from invoke import task
import paramiko
from pathlib import Path
import ruamel.yaml
import semver


class ssh_client_context_manager:
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


class sftp_client_context_manager:
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


def task_ssh(
    *,
    config_key: str,
    instance_dir: str,
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

        task_config = context.config[config_key]
        working_dir = Path(task_config.working_dir)

        with context.cd(working_dir):
            # Launch an external SSH session,
            # which seems more appropriate than attempting via Paramiko.
            context.run(
                command=' '.join([
                    'start',  # Ensures Windows launches ssh outside cmd
                    'ssh',
                    '-l {}'.format(instance_config['instance_user']),
                    '-i {}'.format(Path(instance_dir, instance_config['instance_key_file'])),
                    '-o StrictHostKeyChecking=no',
                    '-o UserKnownHostsFile="{}"'.format(Path(instance_dir, 'known_hosts')),
                    instance_config['instance_ip']
                ]),
                disown=True
            )

    return ssh


def task_ssh_port_forward(
    *,
    config_key: str,
    instance_dir: str,
    instance_config
):
    """
    Create a task to forward a port from the instance.
    """

    @task
    def ssh_port_forward(context, port, local_port=None):
        """
        Forward a port from the instance.

        TODO: Using a privileged local port on Windows requires ssh >= 7.9
        https://github.com/PowerShell/Win32-OpenSSH/issues/1350
        https://github.com/PowerShell/Win32-OpenSSH/releases
        Could not easily determine how to get that installed for Windows.
        Forwarding therefore only works for unprivileged ports.
        """
        print('Creating SSH session to forward port')

        # Map our parameters to a remote and local port
        remote_port = port
        if local_port is None:
            local_port = remote_port

        task_config = context.config[config_key]
        working_dir = Path(task_config.working_dir)

        with context.cd(working_dir):
            # Launch an external SSH session,
            # which seems more appropriate than attempting via Paramiko.
            context.run(
                command=' '.join([
                    'start',  # Ensures Windows launches ssh outside cmd
                    'ssh',
                    '-l {}'.format(instance_config['instance_user']),
                    '-i "{}"'.format(Path(instance_dir, instance_config['instance_key_file'])),
                    '-o StrictHostKeyChecking=no',
                    '-o UserKnownHostsFile="{}"'.format(Path(instance_dir, 'known_hosts')),
                    '-L localhost:{}:localhost:{}'.format(local_port, remote_port),
                    instance_config['instance_ip'],
                    '"' + ' && '.join([
                        'echo \\"Forwarding {}:{}\\"'.format(instance_config['instance_ip'], remote_port),
                        'echo',
                        'echo \\"Connect via localhost:{}\\"'.format(local_port),
                        'echo',
                        'sleep infinity'
                    ]) + '"'
                ]),
                disown=True
            )

    return ssh_port_forward


def task_docker_build(
    *,
    config_key: str,
    instance_dir: str,
    instance_config
):
    @task
    def docker_build(context, build_config):
        """
        Build a Docker image.
        """
        print('Building Docker image')

        task_config = context.config[config_key]
        working_dir = Path(task_config.working_dir)

        # build_config must be a path to a file named build-config.yaml
        if not (Path(build_config).is_file() and Path(build_config).name == 'build-config.yaml'):
            print('No matching build-config.yaml found.')
            return

        # Print the specific chart we will use
        print('Found matching build-config.yaml at: {}'.format(build_config))

        # Load the config
        with open(build_config) as file_config:
            yaml_config = ruamel.yaml.safe_load(file_config)

        # Connect via SSH
        with ssh_client_context_manager(instance_config=instance_config) as ssh_client:
            # Create a staging directory
            ssh_client.exec_command(command=[
                'rm -rf .minikube_helm_staging',
                'mkdir -p .minikube_helm_staging'
            ])

            # Upload the Dockerfile.
            # The configuration 'dockerfile' is a path relative to the location of the build config.
            dockerfile = str(Path(Path(build_config).parent, yaml_config['dockerfile']))
            with sftp_client_context_manager(ssh_client=ssh_client) as sftp_client:
                sftp_client.client.chdir('.minikube_helm_staging')
                sftp_client.client.put(
                    localpath=dockerfile,
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
                        in yaml_config['args'].items()
                    ]),
                    # List of tag parameters
                    ' '.join([
                        '--tag "{}"'.format(tag_current)
                        for tag_current
                        in yaml_config['tags']
                    ]),
                    '.'
                ])
            ])

            # Remove the staging directory
            ssh_client.exec_command(command='rm -rf .minikube_helm_staging')

    return docker_build


def task_helm_install(
    *,
    config_key: str,
    instance_dir: str,
    instance_config
):
    @task
    def helm_install(context, helm_chart):
        """
        Install a chart in the instance.
        """
        print('Installing chart')

        task_config = context.config[config_key]
        working_dir = Path(task_config.working_dir)
        helm_charts_dir = Path(task_config.helm_charts_dir)

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
            helm_chart = Path(working_dir, helm_charts_dir, helm_chart)
        elif (match := re.match('(.+)-([0-9\\.]+)', helm_chart)) is not None:
            # A name including a version (e.g., 'ingress-0.1.0').
            # Use it to reference a file in helm_charts_dir.
            helm_chart = Path(working_dir, helm_charts_dir, '{}.tgz'.format(helm_chart))
        else:
            # A name absent a version (e.g., 'ingress').
            # Find the latest matching chart in helm_charts_dir.
            # Current implemented by looking directly at the files in the repo.
            # Alternatively, could parse and examine `index.yaml`.
            helm_chart_latest = None
            helm_chart_version_latest = None
            for root, dirs, files in os.walk(Path(working_dir, helm_charts_dir)):
                for file_current in files:
                    if (match := re.match('(.+)-([0-9\\.]+)\\.tgz', file_current)) is not None:
                        match_chart = match.group(1)
                        match_version = semver.version.Version.parse(match.group(2))
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
        with ssh_client_context_manager(instance_config=instance_config) as ssh_client:
            # Create a staging directory
            ssh_client.exec_command(command=[
                'rm -rf .minikube_helm_staging',
                'mkdir -p .minikube_helm_staging'
            ])

            # Upload the chart file
            with sftp_client_context_manager(ssh_client=ssh_client) as sftp_client:
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
                '~/.minikube_helm_staging/{}'.format(helm_chart_file_name)
            ]))

            # Remove the staging directory
            ssh_client.exec_command(command='rm -rf .minikube_helm_staging')

    return helm_install


def task_helmfile_apply(
    *,
    config_key: str,
    instance_dir: str,
    instance_config
):
    @task
    def helmfile_apply(context, helmfile):
        """
        Apply a helmfile in the instance.
        """
        print('Applying helmfile')

        task_config = context.config[config_key]
        working_dir = Path(task_config.working_dir)

        # Connect via SSH
        with ssh_client_context_manager(instance_config=instance_config) as ssh_client:
            # Create a staging directory
            ssh_client.exec_command(command=[
                'rm -rf .minikube_helm_staging',
                'mkdir -p .minikube_helm_staging'
            ])

            # Upload the helmfile
            with sftp_client_context_manager(ssh_client=ssh_client) as sftp_client:
                sftp_client.client.chdir('.minikube_helm_staging')
                sftp_client.client.put(
                    localpath=Path(helmfile),
                    remotepath=Path(helmfile).name,
                )

            # Apply the helmfile
            #
            # Use --skip-diff-on-install because:
            # - Missing CRDs will cause helm diff to fail
            # - helm diff output tends to be large for a new install
            ssh_client.exec_command(command=' '.join([
                'helmfile',
                '--file ~/.minikube_helm_staging/{}'.format(Path(helmfile).name),
                'apply',
                '--skip-diff-on-install',
            ]))

            # Remove the staging directory
            ssh_client.exec_command(command='rm -rf .minikube_helm_staging')

    return helmfile_apply


def create_tasks(
    *,
    config_key: str,
    working_dir: str,
    instance_dir: str,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """
    with open(Path(working_dir, instance_dir, 'config.yaml')) as file_config:
        yaml_config = ruamel.yaml.safe_load(file_config)

    instance_name = yaml_config['instance_name']

    ns = Collection(instance_name)

    ssh = task_ssh(
        config_key=config_key,
        instance_dir=instance_dir,
        instance_config=yaml_config
    )
    ns.add_task(ssh)

    ssh_port_forward = task_ssh_port_forward(
        config_key=config_key,
        instance_dir=instance_dir,
        instance_config=yaml_config
    )
    ns.add_task(ssh_port_forward)

    docker_build = task_docker_build(
        config_key=config_key,
        instance_dir=instance_dir,
        instance_config=yaml_config
    )
    ns.add_task(docker_build)

    helm_install = task_helm_install(
        config_key=config_key,
        instance_dir=instance_dir,
        instance_config=yaml_config
    )
    ns.add_task(helm_install)

    helmfile_apply = task_helmfile_apply(
        config_key=config_key,
        instance_dir=instance_dir,
        instance_config=yaml_config
    )
    ns.add_task(helmfile_apply)

    return ns
