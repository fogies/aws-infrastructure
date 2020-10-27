from invoke import Collection

import packer_ami_minikube
import terraform_minikube
import terraform_vpc_packer


ns = Collection()

ns.add_collection(packer_ami_minikube, name='ami-minikube')
ns.configure(packer_ami_minikube.ns.configuration())

ns_terraform_minikube = Collection()
ns_terraform_minikube.add_task(terraform_minikube.create)
ns_terraform_minikube.add_task(terraform_minikube.destroy)
ns_terraform_minikube.add_task(terraform_minikube.ssh)
ns_terraform_minikube.add_task(terraform_minikube.ssh_port_forward)
ns.add_collection(ns_terraform_minikube, name='minikube')

ns.add_collection(terraform_vpc_packer, name='vpc-packer')
ns.configure(terraform_vpc_packer.ns.configuration())
