from invoke import Collection

import packer_ami_minikube
import terraform_minikube
import terraform_vpc_packer


ns = Collection()

ns_packer_ami_minikube = Collection()
ns_packer_ami_minikube.add_task(packer_ami_minikube.build)
ns.add_collection(ns_packer_ami_minikube, name='ami-minikube')

ns_terraform_minikube = Collection()
ns_terraform_minikube.add_task(terraform_minikube.create)
ns_terraform_minikube.add_task(terraform_minikube.destroy)
ns_terraform_minikube.add_task(terraform_minikube.ssh)
ns_terraform_minikube.add_task(terraform_minikube.ssh_port_forward)
ns.add_collection(ns_terraform_minikube, name='minikube')

ns_terraform_vpc_packer = Collection()
ns.add_collection(ns_terraform_vpc_packer, name='vpc-packer')
