import io
import paramiko
from pathlib import Path
import ruamel.yaml
import select
import socketserver
import threading
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
    def load(ssh_config_path: Union[Path, str]):
        ssh_config_path = Path(ssh_config_path)

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


class SSHClient:
    """
    Client for connecting, using, and destroying an SSH connection.
    """

    _ssh_config: SSHConfig

    _paramiko_ssh_client: paramiko.SSHClient

    def __init__(self, *, ssh_config: SSHConfig):
        self._ssh_config = ssh_config

        self._paramiko_ssh_client = None

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

        stdin, stdout, stderr = self._paramiko_ssh_client.exec_command(
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

    def open(self):
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

        self._paramiko_ssh_client = client

    def close(self):
        """
        Destroy the SSH connection.
        """
        self._paramiko_ssh_client.close()
        self._paramiko_ssh_client = None

    @property
    def paramiko_ssh_client(self) -> paramiko.SSHClient:
        return self._paramiko_ssh_client


class SSHClientContextManager:
    """
    Context manager for connecting, using, and closing an SSH client.
    """

    _ssh_client: SSHClient

    def __init__(self, *, ssh_config: SSHConfig):
        self._ssh_client = SSHClient(ssh_config=ssh_config)

    def __enter__(self) -> SSHClient:
        self._ssh_client.open()

        return self._ssh_client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ssh_client.close()


class SFTPClient:
    """
    Context manager for connecting, using, and destroying an SFTP client.
    """

    _ssh_client: SSHClient
    _paramiko_sftp_client: paramiko.SFTPClient

    def __init__(self, *, ssh_client: SSHClient):
        self._ssh_client = ssh_client
        self._sftp_client = None

    def open(self):
        """
        Open an SFTP connection.
        """
        self._paramiko_sftp_client = self._ssh_client.paramiko_ssh_client.open_sftp()

    def close(self):
        """
        Close an SFTP connection.
        """
        self._paramiko_sftp_client.close()
        self._paramiko_sftp_client = None

    @property
    def paramiko_sftp_client(self) -> paramiko.SFTPClient:
        return self._paramiko_sftp_client


class SFTPClientContextManager:
    """
    Context manager for connecting, using, and closing an SFTP client.
    """

    _sftp_client: SFTPClient

    def __init__(self, *, ssh_client: SSHClient):
        self._sftp_client = SFTPClient(ssh_client=ssh_client)

    def __enter__(self) -> SFTPClient:
        self._sftp_client.open()

        return self._sftp_client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._sftp_client.close()


class SSHPortForward:
    """
    Forward a port through an ssh client.
    """

    _ssh_client: SSHClient
    _remote_host: str
    _remote_port: int
    _requested_local_port: int

    _server: socketserver.ThreadingTCPServer

    def __init__(
        self,
        *,
        ssh_client: SSHClient,
        remote_host: str,
        remote_port: int,
        local_port: int = 0,
    ):
        self._ssh_client = ssh_client
        self._remote_host = remote_host
        self._remote_port = remote_port
        self._requested_local_port = local_port

        self._server = None

    def _create_handler(self, ssh_client: SSHClient, remote_host: int, remote_port: int):
        class Handler(socketserver.BaseRequestHandler):
            _ssh_client: SSHClient = ssh_client
            _remote_port: int = remote_port

            def handle(self):
                channel = self._ssh_client.paramiko_ssh_client.get_transport().open_channel(
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

    def serve_forever(self):
        """
        Forward incoming requests forever.
        """
        self._server.serve_forever()

    def open(self):
        """
        Start the port forwarding server.
        """
        self._server = socketserver.ThreadingTCPServer(
            server_address=('localhost', self._requested_local_port),
            RequestHandlerClass=self._create_handler(self._ssh_client, self._remote_host, self._remote_port),
        )

        threading.Thread(target=self.serve_forever).start()

        print('Forwarding local port {} to remote {}:{}'.format(self.local_port, self.remote_host, self.remote_port))

    def close(self):
        """
        Stop the port forwarding server.
        """
        self._server.shutdown()
        self._server = None

    @property
    def local_port(self) -> str:
        # Obtain the port from the server,
        # so that providing local port of 0 allows automatically choosing an open port
        (server_host, server_port) = self._server.server_address

        return server_port

    @property
    def remote_host(self) -> str:
        return self._remote_host

    @property
    def remote_port(self) -> str:
        return self._remote_port


class SSHPortForwardContextManager:
    """
    Context manager for connecting, using, and closing a port forward.
    """

    _ssh_port_forward: SSHPortForward

    def __init__(
        self,
        *,
        ssh_client: SSHClientContextManager,
        remote_host: str,
        remote_port: int,
        local_port: int = 0,
    ):
        self._ssh_port_forward = SSHPortForward(
            ssh_client=ssh_client,
            remote_host=remote_host,
            remote_port=remote_port,
            local_port=local_port,
        )

    def __enter__(self):
        self._ssh_port_forward.open()

        return self._ssh_port_forward

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ssh_port_forward.close()
