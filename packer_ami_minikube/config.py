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
    'version_helm': 'v3.5.4',
    # Version of helmdiff to install.
    'version_helmdiff': 'v3.1.3',
    # Version of helmfile to install.
    'version_helmfile': 'v0.139.3',

    # Version of Kubernetes to install.
    'version_kubernetes': 'v1.21.0',

    # Version of minikube to install.
    'version_minikube': 'v1.20.0',

    # Version name of Ubuntu.
    'version_ubuntu_name': 'focal',
    # Version number of Ubuntu.
    'version_ubuntu_number': '20.04',
}

#
# Simple configuration fields that are unique to each build.
#
# Values specified here will override any values specified in BUILD_CONFIG_SHARED.
#
# Keys specified here will become part of AMI names. Prefer `-` separators.
#
BUILD_CONFIG_INSTANCES = {
    'amd64-medium': {
        # Type of instance in which to build the image.
        'aws_instance_architecture': 'amd64',
        # Architecture of instance in which to build the image.
        'aws_instance_type': 't3.medium',

        # Filter applied to name of the source AMI.
        'source_ami_filter_name': 'ubuntu/images/hvm-ssd/ubuntu-{}-{}-{}-server-*'.format(
            BUILD_CONFIG_SHARED['version_ubuntu_name'],
            BUILD_CONFIG_SHARED['version_ubuntu_number'],
            'amd64',
        ),

        # Memory to allocate to Minikube.
        'minikube_memory': '2g',
    },
    'amd64-large': {
        # Type of instance in which to build the image.
        'aws_instance_architecture': 'amd64',
        # Architecture of instance in which to build the image.
        'aws_instance_type': 't3.large',

        # Filter applied to name of the source AMI.
        'source_ami_filter_name': 'ubuntu/images/hvm-ssd/ubuntu-{}-{}-{}-server-*'.format(
            BUILD_CONFIG_SHARED['version_ubuntu_name'],
            BUILD_CONFIG_SHARED['version_ubuntu_number'],
            'amd64',
        ),

        # Memory to allocate to Minikube.
        'minikube_memory': '6g',
    },
    # TODO: arm64 currently fails due to lack of arm64 support in helmdiff
    #
    # 'arm64': {
    #     # Type of instance in which to build the image.
    #     'aws_instance_architecture': 'arm64',
    #     # Architecture of instance in which to build the image.
    #     'aws_instance_type': 't4g.medium',
    #
    #     # Filter applied to name of the source AMI.
    #     'source_ami_filter_name': 'ubuntu/images/hvm-ssd/ubuntu-{}-{}-{}-server-*'.format(
    #         BUILD_CONFIG_SHARED['version_ubuntu_name'],
    #         BUILD_CONFIG_SHARED['version_ubuntu_number'],
    #         'arm64',
    #     ),
    #
    #     # Memory to allocate to Minikube.
    #     'minikube_memory': '2g',
    # },
}

#
# Obtain BUILD_CONFIG by merging each instance of BUILD_CONFIG_INSTANCES into BUILD_CONFIG_SHARED
#
BUILD_CONFIG = {
    build_config_key: build_config | BUILD_CONFIG_SHARED
    for build_config_key, build_config
    in BUILD_CONFIG_INSTANCES.items()
}

#
# Add additional fields that are computed based on a specified build configuration.
#
BUILD_CONFIG = {
    build_config_key: build_config | {
        # Name to assign the build AMI.
        'build_ami_name': 'minikube-{}-{}'.format(
            build_config_key,
            TIMESTAMP_NOW,
        ),
    }
    for build_config_key, build_config
    in BUILD_CONFIG.items()
}


