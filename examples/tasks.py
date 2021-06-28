from invoke import Collection

from aws_infrastructure.tasks import compose_collection
import examples.minikube_helm.tasks
import examples.minikube_helm_multiple.tasks

# Build our task collection
ns = Collection('examples')

# Compose from minikube-helm
compose_collection(ns, examples.minikube_helm.tasks.ns)

# Compose from minikube-helm-multiple
compose_collection(ns, examples.minikube_helm_multiple.tasks.ns)
