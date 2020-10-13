from invoke import Collection

import ami_minikube
import terraform_vpc_packer


ns = Collection()
ns.add_collection(ami_minikube)
ns.add_collection(terraform_vpc_packer, name='vpc-packer')
