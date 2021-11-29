from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.aws_configure
import aws_infrastructure.tasks.library.color
import aws_infrastructure.tasks.library.config
from invoke import Collection

import examples.tasks
import tasks.aws
import tasks.helm
import tasks.packer_ami_minikube
import tasks.terraform_vpc_packer

# Enable color
aws_infrastructure.tasks.library.color.enable_color()
# Apply the current AWS configuration
aws_infrastructure.tasks.library.aws_configure.apply_aws_env(aws_env_path=tasks.aws.AWS_ENV_PATH)

# Build our task collection
ns = Collection()

# Tasks for Invoke configuration
compose_collection(
    ns,
    aws_infrastructure.tasks.library.config.create_tasks(),
    name='config'
)

# Compose from aws.py
compose_collection(ns, tasks.aws.ns, name='aws')

# Compose from helm.py
compose_collection(ns, tasks.helm.ns, name='helm')

# Compose from packer_ami_minikube.py
compose_collection(ns, tasks.packer_ami_minikube.ns, name='ami-minikube')

# Compose from terraform_vpc_packer.py
compose_collection(ns, tasks.terraform_vpc_packer.ns, name='vpc-packer')

# Examples include a tasks.py, so that each example directory is more self-contained.
# Compose from example-related tasks gathered in examples/tasks.py.
compose_collection(ns, examples.tasks.ns, name='examples')
