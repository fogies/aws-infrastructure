from collections import namedtuple
from invoke import task
import io
import paramiko
from pathlib import Path
import ruamel.yaml
import select
import socketserver
from typing import List
from typing import Union


class SSHConfig:
    """
    Configuration for SSH connection to an instance.
    """
    def __init__(self, *, ssh_config_path: Path):
        with open(ssh_config_path) as file_ssh_config:
            yaml_config = ruamel.yaml.safe_load(file_ssh_config)

        self._ip = yaml_config['ip']
        self._key = yaml_config['key']
        self._key_file = yaml_config['key_file']
        self._user = yaml_config['user']

    @property
    def ip(self):
        return self._ip

    @property
    def key(self):
        return self._key

    @property
    def key_file(self):
        return self._key_file

    @property
    def user(self):
        return self._user


class SSHClientContextManager:
    """
    Context manager for connecting, using, and destroying an SSH client.
    """
    def __init__(self, *, ssh_config: SSHConfig):
        self._ssh_config: SSHConfig = ssh_config
        self._client: paramiko.SSHClient = None

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
            hostname=self._ssh_config.ip,
            username=self._ssh_config.user,
            pkey=paramiko.rsakey.RSAKey.from_private_key(io.StringIO(self._ssh_config.key))
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
    def __init__(self, *, ssh_client, remote_host, remote_port, local_port):
        self._ssh_client = ssh_client
        self._remote_host = remote_host
        self._remote_port = remote_port
        self._local_port = local_port
        self._server = None

    def __enter__(self):
        self._port_forward_start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._port_forward_destroy()

    def _create_handler(self, ssh_client, remote_host, remote_port):
        class Handler(socketserver.BaseRequestHandler):
            _ssh_client = ssh_client
            _remote_port = remote_port

            def handle(self):
                channel = self._ssh_client.get_transport().open_channel(
                    kind='direct-tcpip',
                    dest_addr=(remote_host, remote_port),
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
            RequestHandlerClass=self._create_handler(self._ssh_client.client, self._remote_host, self._remote_port),
        )

        print('Forwarding local port {} to remote port {}'.format(self._local_port, self._remote_port))

    def _port_forward_destroy(self):
        """
        Stop the port forwarding server.

        In practice it will already be stopped, as this code is only reached by a keyboard interrupt.
        """
        self._server.shutdown()
        self._server = None


def task_ssh(
    *,
    config_key: str,
    ssh_config_path: Union[Path, str],
):
    """
    Create a task to open an SSH session to the instance.
    """

    ssh_config_path = Path(ssh_config_path)

    @task
    def ssh(context):
        """
        Open an SSH session to the instance.
        """
        print('Creating SSH session')

        # Load the SSH config
        ssh_config = SSHConfig(ssh_config_path=ssh_config_path)

        # Launch an external SSH session,
        # which seems more appropriate than attempting via Paramiko.
        context.run(
            command=' '.join([
                'start',  # Ensures Windows launches ssh outside cmd
                          # This has been only way to obtain a proper terminal
                'ssh',
                '-l {}'.format(ssh_config.user),
                '-i {}'.format(Path(ssh_config_path.parent, ssh_config.key_file)),
                '-o StrictHostKeyChecking=no',
                '-o UserKnownHostsFile="{}"'.format(Path(ssh_config_path.parent, 'known_hosts')),
                ssh_config.ip
            ]),
            disown=True
        )

    return ssh


def task_ssh_port_forward(
    *,
    config_key: str,
    ssh_config_path: Union[Path, str],
):
    """
    Create a task to forward a port from the instance.
    """

    ssh_config_path = Path(ssh_config_path)

    @task
    def ssh_port_forward(context, port, host=None, local_port=None):
        """
        Forward a port from a remote host accessible by the instance.
        """

        # Load the SSH config
        ssh_config = SSHConfig(ssh_config_path=ssh_config_path)

        # Remote port is required
        remote_port = int(port)

        # If no remote host is provided, use 'localhost'
        if host:
            remote_host = host
        else:
            remote_host = 'localhost'

        # If no local port is provided, use the same as the remote port
        if local_port:
            local_port = int(local_port)
        else:
            local_port = remote_port

        # Connect via SSH
        with SSHClientContextManager(ssh_config=ssh_config) as ssh_client:
            # Initiate port forwarding
            with PortForwardContextManager(
                ssh_client=ssh_client,
                local_port=local_port,
                remote_host=remote_host,
                remote_port=remote_port
            ) as port_forward:
                port_forward.forward_forever()

    return ssh_port_forward
