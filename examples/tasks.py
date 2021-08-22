from invoke import Collection

from aws_infrastructure.tasks import compose_collection
import examples.codebuild.tasks
import examples.ecr.tasks
import examples.minikube_helm.tasks
import examples.minikube_helm_multiple.tasks

# Build our task collection
ns = Collection('examples')

# Compose from codebuild
compose_collection(ns, examples.codebuild.tasks.ns)

# Compose from ecr-simple
compose_collection(ns, examples.ecr.tasks.ns)

# Compose from minikube-helm
compose_collection(ns, examples.minikube_helm.tasks.ns)

# Compose from minikube-helm-multiple
compose_collection(ns, examples.minikube_helm_multiple.tasks.ns)
