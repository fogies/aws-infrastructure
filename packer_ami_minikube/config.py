import datetime

#
# Timestamp that will be applied to this build.
#
TIMESTAMP_NOW = datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')

#
# Simple configuration fields that are shared across all builds.
#
BUILD_CONFIG_SHARED = {
    # Region in which to build the image.
    'aws_region': 'us-east-1',

    # List of allowable owner IDs of the source AMI.
    'source_ami_filter_owners': [
        # IDs are quoted to ensure processing as a string.
        '"099720109477"',  # Ubuntu ID
    ],

    # Version of helm to install.
    'version_helm': 'v3.5.2',
    # Version of helmdiff to install.
    'version_helmdiff': 'v3.1.3',
    # Version of helmfile to install.
    'version_helmfile': 'v0.138.4',

    # Version of kubectl to install.
    'version_kubectl': 'v1.20.2',

    # Version of minikube to install.
    'version_minikube': 'v1.17.1',

    # Name used by desired version of Ubuntu.
    'version_ubuntu_name': 'focal',
}

#
# Simple configuration fields that are unique to each build.
#
# Values specified here will override any values specified in BUILD_CONFIG_SHARED.
#
BUILD_CONFIG_INSTANCES = {
    'amd64': {
        # Type of instance in which to build the image.
        'aws_instance_architecture': 'amd64',
        # Architecture of instance in which to build the image.
        'aws_instance_type': 't3.medium',

        # Filter applied to name of the source AMI.
        'source_ami_filter_name': 'ubuntu/images/hvm-ssd/ubuntu-focal-20.04-{}-server-*'.format(
            'amd64',
        ),

        # Memory to allocate to Minikube.
        'minikube_memory': '2g',

        # Name to assign the build AMI.
        'build_ami_name': 'ami-minikube-{}-{}'.format(
            'amd64',
            TIMESTAMP_NOW,
        ),
    },
    # 'arm64': {
    #     # Type of instance in which to build the image.
    #     'aws_instance_architecture': 'arm64',
    #     # Architecture of instance in which to build the image.
    #     'aws_instance_type': 't4g.medium',
    #
    #     # Filter applied to name of the source AMI.
    #     'source_ami_filter_name': "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-arm64-server-*",
    # },
}

#
# Obtain BUILD_CONFIG by merging each instance of BUILD_CONFIG_INSTANCES into BUILD_CONFIG_SHARED
#
BUILD_CONFIG = {
    # TODO: Python 3.9 provides a | operator for this purpose, if we want to require Python 3.9
    build_config_key: {**build_config_value, **BUILD_CONFIG_SHARED}
    for build_config_key, build_config_value
    in BUILD_CONFIG_INSTANCES.items()
}
