from invoke import Collection
import examples.minikube_helm.tasks
import examples.minikube_helm_multiple.tasks

# Build our task collection
ns = Collection('examples')

# Tasks for minikube-helm
ns_terraform_minikube_helm_example = examples.minikube_helm.tasks.ns
ns.add_collection(ns_terraform_minikube_helm_example)
ns.configure(ns_terraform_minikube_helm_example.configuration())

# Tasks for minikube-helm-multiple
ns_terraform_minikube_helm_example_multiple = examples.minikube_helm_multiple.tasks.ns
ns.add_collection(ns_terraform_minikube_helm_example_multiple)
ns.configure(ns_terraform_minikube_helm_example_multiple.configuration())
