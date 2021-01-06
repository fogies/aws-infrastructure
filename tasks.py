import aws_infrastructure.task_templates.config
import aws_infrastructure.task_templates.helm
from invoke import Collection
import packer_ami_minikube.tasks
import terraform_minikube_helm_example.tasks
import terraform_vpc_packer.tasks

# Build our task collection
ns = Collection()

# Tasks for Invoke configuration
ns_config = aws_infrastructure.task_templates.config.create_tasks()
ns.add_collection(ns_config)
ns.configure(ns_config.configuration())

# Tasks for Helm
HELM_CONFIG_KEY = 'helm'

ns_helm = aws_infrastructure.task_templates.helm.create_tasks(
    config_key=HELM_CONFIG_KEY
)
ns.add_collection(ns_helm)
ns.configure({
    HELM_CONFIG_KEY: {
        'bin_dir': 'bin',
        'helm_charts_dir': 'helm',
        'helm_repo_dir': 'helm_repo',
        'helm_repo_staging_dir': 'helm_repo_staging',
    }
})

# Tasks for ami-minikube
ns_packer_ami_minikube = packer_ami_minikube.tasks.ns
ns.add_collection(ns_packer_ami_minikube)
ns.configure(ns_packer_ami_minikube.configuration())

# Tasks for minikube-helm-example
ns_terraform_minikube_helm_example = terraform_minikube_helm_example.tasks.ns
ns.add_collection(ns_terraform_minikube_helm_example)
ns.configure(ns_terraform_minikube_helm_example.configuration())

# Tasks for vpc-packer
ns_terraform_vpc_packer = terraform_vpc_packer.tasks.ns
ns.add_collection(ns_terraform_vpc_packer)
ns.configure(ns_terraform_vpc_packer.configuration())
