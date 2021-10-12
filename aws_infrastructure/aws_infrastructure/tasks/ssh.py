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

    _ip: str
    _key: str
    _key_file: Path
    _user: str

    def __init__(self, *, ip: str, key: str, key_file: Union[Path, str], user: str):
        self._ip = ip
        self._key = key
        self._key_file = Path(key_file)
        self._user = user

    @staticmethod
    def load(ssh_config_path: Path):
        with open(ssh_config_path) as ssh_config_file:
            yaml_config = ruamel.yaml.safe_load(ssh_config_file)

        return SSHConfig(
            ip = yaml_config['ip'],
            key = yaml_config['key'],
            key_file = yaml_config['key_file'],
            user = yaml_config['user'],
        )

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def key(self) -> str:
        return self._key

    @property
    def key_file(self) -> Path:
        return self._key_file

    @property
    def user(self) -> str:
        return self._user


class SSHClientContextManager:
    """
    Context manager for connecting, using, and destroying an SSH client.
    """

    _ssh_config: SSHConfig
    _client: paramiko.SSHClient

    def __init__(self, *, ssh_config: SSHConfig):
        self._ssh_config = ssh_config
        self._client = None

    def __enter__(self):
        self._ssh_connect()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ssh_destroy()

    @property
    def client(self) -> paramiko.SSHClient:
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
    def client(self) -> paramiko.SFTPClient:
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


class SSHPortForwardContextManager:
    """
    Context manager for forwarding a port through an ssh client.
    """

    _ssh_client: SSHClientContextManager
    _remote_host: str
    _remote_port: int
    _local_port: int
    _server: socketserver.ThreadingTCPServer

    def __init__(self, *, ssh_client: SSHClientContextManager, remote_host: str, remote_port: int, local_port: int):
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
