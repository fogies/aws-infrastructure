#
# Variables related to the AWS instance.
#

variable "aws_region" {
  # Region in which to build the image.
  #
  # Typical value is 'us-east-1'.

  type = string
}

variable "aws_instance_type" {
  # Type of instance in which to build the image.
  #
  # Instance types with less than 4g of memory cause Minikube configuration failures.
  #
  # A corresponding value must be set for "aws_instance_architecture".
  # A corresponding value must be set for "source_ami_filter_name".
  # A corresponding value must be set for "minikube_memory".
  #
  # Typical value is 't3.medium' (amd64) or larger.
  # Typical value is 't4g.medium' (arm64) or larger.
  #
  # TODO: "arm64" not supported pending Minikube docker driver
  #       https://minikube.sigs.k8s.io/docs/drivers/docker/

  type = string
}

variable "aws_instance_architecture" {
  # Architecture of instance in which to build the image.
  #
  # Valid values are 'amd64' or 'arm64'.

  type = string
}

#
# Variables related to the source AMI.
#

variable "source_ami_filter_owners" {
  # List of allowable owner IDs of the source AMI.
  #
  # Typical value is a list containing the single element "099720109477", which is the Ubuntu ID.

  type = list(string)
}

variable "source_ami_filter_name" {
  # Filter applied to name of the source AMI.
  #
  # Typical values:
  #
  # Ubuntu 20.04 for amd64 architecture
  # - "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"
  #
  # Ubuntu 20.04 for arm64 architecture
  # - "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-arm64-server-*"
  #
  # Ubuntu Minimal 20.04 for amd64 architecture
  # - "ubuntu-minimal/images/hvm-ssd/ubuntu-focal-20.04-amd64-minimal-*"

  type = string
}

#
# Variables related to Minikube configuration.
#

variable "minikube_memory" {
  # Memory to allocate to Minikube.
  # Provided as a string to `minikube start`.
  #
  # Typical value is 2g less than instance available memory.
  # Format of a typical value resembles '2g'.

  type = string
}

#
# Variables related to versions.
#

variable "version_helm" {
  # Version of helm to install.
  #
  # Format of a typical value resembles 'v3.5.2'.

  type = string
}

variable "version_helmdiff" {
  # Version of helmdiff to install.
  #
  # Format of a typical value resembles 'v3.1.3'.

  type = string
}

variable "version_helmfile" {
  # Version of helmfile to install.
  #
  # Format of a typical value resembles 'v0.138.4'.

  type = string
}

variable "version_kubectl" {
  # Version of kubectl to install.
  #
  # Format of a typical value resembles 'v1.20.2'.

  type = string
}

variable "version_minikube" {
  # Version of minikube to install.
  #
  # Format of a typical value resembles 'v1.17.1'.

  type = string
}

variable "version_ubuntu_name" {
  # Name used by desired version of Ubuntu.
  #
  # Typical value is 'focal'.

  type = string
}

#
# Variables related to the build AMI.
#

variable "build_ami_name" {
  # Name to assign the build AMI.
  #
  # Typical value is calculated based on other configuration values.

  type = string
}

