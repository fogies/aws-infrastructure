# Ingress

Configures a local Docker registry, available at registry.local.

## Requirements
  
Only one release may be installed, because this creates global resources that may conflict.

Assumes prior installation of ingress.

Assumes a host has mapped registry.local to the local port.
packer_ami_minikube does this within Minikube using ansible_minikube_registry.yml.

## Versions

### 0.1.0

- Initial version.
