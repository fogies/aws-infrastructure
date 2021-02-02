import os
import re

from invoke import Collection
from invoke import task
import ruamel.yaml


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
        print('Creating SSH Session')

        config = context.config[config_key]
        working_dir = os.path.normpath(config.working_dir)

        # Will be interpreted within working_dir per context below
        identity_file = os.path.normpath(os.path.join(
            instance_dir,
            instance_config['instance_identity_file']
        ))

        # Will be interpreted within working_dir per context below
        hosts_file = os.path.normpath(os.path.join(
            instance_dir,
            'known_hosts'
        ))

        ip = instance_config['instance_ip']

        with context.cd(working_dir):
            context.run(
                command=' '.join([
                    'start',  # Ensures Windows launches ssh outside cmd
                    'ssh',
                    '-l ubuntu',
                    '-i {}'.format(identity_file),
                    '-o StrictHostKeyChecking=no',
                    '-o UserKnownHostsFile="{}"'.format(hosts_file),
                    ip
                ]),
                disown=True
            )

    return ssh


# TODO: Using a privileged local port on Windows requires ssh >= 7.9
# https://github.com/PowerShell/Win32-OpenSSH/issues/1350
# https://github.com/PowerShell/Win32-OpenSSH/releases
# Could not easily determine how to get that installed for Windows.
# Forwarding therefore only works for unprivileged ports.
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
        """
        print('Creating SSH Session to Forward Port')

        config = context.config[config_key]
        working_dir = os.path.normpath(config.working_dir)

        # Will be interpreted within working_dir per context below
        identity_file = os.path.normpath(os.path.join(
            instance_dir,
            instance_config['instance_identity_file']
        ))

        # Will be interpreted within working_dir per context below
        hosts_file = os.path.normpath(os.path.join(
            instance_dir,
            'known_hosts'
        ))

        ip = instance_config['instance_ip']

        with context.cd(working_dir):
            remote_port = port
            if local_port is None:
                local_port = remote_port

            context.run(
                command=' '.join([
                    'start',  # Ensures Windows launches ssh outside cmd
                    'ssh',
                    '-l ubuntu',
                    '-i {}'.format(identity_file),
                    '-o StrictHostKeyChecking=no',
                    '-o UserKnownHostsFile="{}"'.format(hosts_file),
                    '-L localhost:{}:localhost:{}'.format(local_port, remote_port),
                    ip,
                    '"' + ' && '.join([
                        'echo \\"Forwarding {}:{}\\"'.format(ip, remote_port),
                        'echo',
                        'echo \\"Connect via localhost:{}\\"'.format(local_port),
                        'echo',
                        'sleep infinity'
                    ]) + '"'
                ]),
                disown=True
            )

    return ssh_port_forward


def task_helm_install_chart(
    *,
    config_key: str,
    instance_dir: str,
    instance_config
):
    @task
    def helm_install_chart(context, helm_chart_file):
        """
        Install a chart in the instance.
        """
        print('Installing Chart')

        config = context.config[config_key]
        working_dir = os.path.normpath(config.working_dir)
        bin_helm = os.path.normpath(os.path.join(config.bin_dir, 'helm.exe'))
        helm_charts_dir = os.path.normpath(config.helm_charts_dir)

        # Will be interpreted within working_dir per context below
        identity_file = os.path.normpath(os.path.join(
            instance_dir,
            instance_config['instance_identity_file']
        ))

        # Will be interpreted within working_dir per context below
        hosts_file = os.path.normpath(os.path.join(
            instance_dir,
            'known_hosts'
        ))

        ip = instance_config['instance_ip']

        # Will be interpreted within working_dir per context below
        helm_chart_path = os.path.normpath(os.path.join(
            helm_charts_dir,
            helm_chart_file
        ))

        # Parse the chart file name into its parts
        match = re.match('(.+)-(.+)\\.tgz', helm_chart_file)
        chart_name = match.group(1)
        chart_version = match.group(2)

        with context.cd(working_dir):
            # Ensure a staging directory exists
            context.run(
                command=' '.join([
                    'ssh',
                    '-l ubuntu',
                    '-i "{}"'.format(identity_file),
                    '-o StrictHostKeyChecking=no',
                    '-o UserKnownHostsFile="{}"'.format(hosts_file),
                    ip,
                    '"' + ' && '.join([
                        'mkdir -p .minikube_helm_staging'
                    ]) + '"'
                ]),
            )

            # Upload the chart into our staging directory
            context.run(
                command=' '.join([
                    'scp',
                    '-q',
                    '-i {}'.format(identity_file),
                    '-o StrictHostKeyChecking=no',
                    '-o UserKnownHostsFile="{}"'.format(hosts_file),
                    '"{}"'.format(helm_chart_path),
                    'ubuntu@{}:~/.minikube_helm_staging'.format(ip)
                ]),
            )

            # Apply the chart
            # Skip CRDs to require pattern of installing them separately
            context.run(
                command=' '.join([
                    'ssh',
                    '-l ubuntu',
                    '-i {}'.format(identity_file),
                    '-o StrictHostKeyChecking=no',
                    '-o UserKnownHostsFile="{}"'.format(hosts_file),
                    ip,
                    '"' + ' && '.join([
                        ' '.join([
                            'helm',
                            'upgrade',
                            '--install',
                            '--skip-crds',
                            chart_name,
                            '~/.minikube_helm_staging/{}'.format(helm_chart_file)
                        ])
                    ]) + '"'
                ]),
            )

    return helm_install_chart


def create_tasks(
        *,
        config_key: str,
        working_dir: str,
        instance_dir: str,
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    instance_dir_path = os.path.normpath(os.path.join(working_dir, instance_dir))
    instance_config_path = os.path.normpath(os.path.join(instance_dir_path, 'config.yaml'))

    with open(instance_config_path) as file_config:
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

    helm_install_chart = task_helm_install_chart(
        config_key=config_key,
        instance_dir=instance_dir,
        instance_config=yaml_config
    )
    ns.add_task(helm_install_chart)

    return ns
