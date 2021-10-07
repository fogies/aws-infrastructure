from invoke import task
import os
from pathlib import Path
import re
import semver

import aws_infrastructure.tasks.library.instance_ssh

def task_helm_install(
    *,
    config_key: str,
    helm_repo_dir: Path,
    ssh_config_path: Path,
    dir_staging_remote: Path,
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
            helm_chart = Path(helm_repo_dir, helm_chart)
        elif (match := re.match('(.+)-([0-9\\.]+)', helm_chart)) is not None:
            # A name including a version (e.g., 'ingress-0.1.0').
            # Use it to reference a file in helm_charts_dir.
            helm_chart = Path(helm_repo_dir, '{}.tgz'.format(helm_chart))
        else:
            # A name absent a version (e.g., 'ingress').
            # Find the latest matching chart in helm_charts_dir.
            # Current implemented by looking directly at the files in the repo.
            # Alternatively, could parse and examine `index.yaml`.
            helm_chart_latest = None
            helm_chart_version_latest = None
            for root, dirs, files in os.walk(helm_repo_dir):
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
        ssh_config = aws_infrastructure.tasks.library.instance_ssh.SSHConfig(ssh_config_path=ssh_config_path)
        with aws_infrastructure.tasks.library.instance_ssh.SSHClientContextManager(ssh_config=ssh_config) as ssh_client:
            # Create a staging directory
            ssh_client.exec_command(command=[
                'rm -rf {}'.format(dir_staging_remote.as_posix()),
                'mkdir -p {}'.format(dir_staging_remote.as_posix()),
            ])

            # Upload the chart file
            with aws_infrastructure.tasks.library.instance_ssh.SFTPClientContextManager(ssh_client=ssh_client) as sftp_client:
                sftp_client.client.chdir(dir_staging_remote.as_posix())
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
                Path(dir_staging_remote, helm_chart_file_name).as_posix(),
            ]))

            # Remove the staging directory
            ssh_client.exec_command(command='rm -rf {}'.format(dir_staging_remote.as_posix()))

    return helm_install
