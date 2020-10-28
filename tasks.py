from invoke import Collection

import packer_ami_minikube
import terraform_minikube_helm_example
import terraform_vpc_packer

ns = Collection()

ns.add_collection(packer_ami_minikube.ns, name='ami-minikube')
ns.configure(packer_ami_minikube.ns.configuration())

ns.add_collection(terraform_minikube_helm_example.ns, name='minikube-helm-example')
ns.configure(terraform_minikube_helm_example.ns.configuration())

ns.add_collection(terraform_vpc_packer.ns, name='vpc-packer')
ns.configure(terraform_vpc_packer.ns.configuration())
