/*
 * Command flags provided to each Ansible provisioner.
 */
local "ansible_command" {
  expression = "PYTHONUNBUFFERED=1 ansible-playbook"
}

/*
 * Extra arguments provided to each Ansible provisioner, giving access to our desired variables.
 */
local "ansible_extra_arguments" {
  expression = [
    "--extra-vars",
    format("'%v'",
      jsonencode({
        "aws_instance_architecture"="${ var.aws_instance_architecture }",
        "minikube_memory"="${ var.minikube_memory }",

        "version_helm"="${ var.version_helm }",
        "version_helmdiff"="${ var.version_helmdiff }",
        "version_helmfile"="${ var.version_helmfile }",
        "version_kubectl"="${ var.version_kubectl }",
        "version_minikube"="${ var.version_minikube }",
        "version_ubuntu_name"="${ var.version_ubuntu_name }",
      })
    ),
  ]
}

