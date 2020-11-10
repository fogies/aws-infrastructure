variable "ami_architecture" {
  # Valid value is "amd64"
  # TODO: "arm64" not supported pending Minikube docker driver
  #       https://minikube.sigs.k8s.io/docs/drivers/docker/
  type = string
}
