from collections import namedtuple
from invoke import task
from pathlib import Path
from typing import List
from typing import Union

import aws_infrastructure.tasks.ssh

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
        ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(ssh_config_path=ssh_config_path)

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
        ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(ssh_config_path=ssh_config_path)

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
        with aws_infrastructure.tasks.ssh.SSHClientContextManager(ssh_config=ssh_config) as ssh_client:
            # Initiate port forwarding
            with aws_infrastructure.tasks.ssh.SSHPortForwardContextManager(
                ssh_client=ssh_client,
                local_port=local_port,
                remote_host=remote_host,
                remote_port=remote_port
            ) as port_forward:
                port_forward.forward_forever()

    return ssh_port_forward
