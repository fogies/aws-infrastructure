from invoke import Collection

import packer_ami_minikube
import terraform_vpc_packer


ns = Collection()
ns.add_collection(packer_ami_minikube, name='ami-minikube')
ns.add_collection(terraform_vpc_packer, name='vpc-packer')
