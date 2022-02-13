/*
 * Steps to provision the AMI.
 */
build {
  sources = [
    "source.amazon-ebs.minikube"
  ]

  /*
   * Apply any updates
   */
  provisioner "shell" {
    inline = [
      "sudo apt-get --quiet --assume-yes update",
      "sudo apt-get --quiet --assume-yes upgrade",
	]
	
	# Allow retries because of apt-get state errors
	max_retries = 5
  }

  /*
   * Install Ansible, available as a package in Ubuntu 20
   */
  provisioner "shell" {
    inline = [
      "sudo apt-get --quiet --assume-yes update",
      "sudo apt-get --quiet --assume-yes install ansible",
	]

	# Allow retries because of apt-get state errors
	max_retries = 5
  }

  /*
   * Configure Volume for Docker Storage
   */
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_docker_volume.yaml"

    command = local.ansible_command
    extra_arguments = local.ansible_extra_arguments
  }

  /*
   * Install Docker
   */
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_docker.yaml"

    command = local.ansible_command
    extra_arguments = local.ansible_extra_arguments
  }

  /*
   * Reboot to apply group permissions for non-sudo Docker access
   */
  provisioner "shell" {
    inline = [
	  "sudo reboot",
	]
	
	# Expect a potential disconnect because of the reboot
	expect_disconnect = true
  }

  /*
   * Confirm non-sudo Docker access
   */
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_docker_confirm.yaml"
	
    command = local.ansible_command
    extra_arguments = local.ansible_extra_arguments

	# Pause and retries to allow for reboot
	pause_before = "5s"
	max_retries = 10
  }

  /*
   * Install Minikube
   */
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_minikube.yaml"

    command = local.ansible_command
    extra_arguments = local.ansible_extra_arguments
  }

  /*
   * Expose Minikube ports for ingress
   */
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_minikube_ingress_ports.yaml"

    command = local.ansible_command
    extra_arguments = local.ansible_extra_arguments
  }

  /*
   * Install Helm
   */
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_helm.yaml"

    command = local.ansible_command
    extra_arguments = local.ansible_extra_arguments
  }

  /*
   * Output manifest for recovering resulting AMI
   */
  post-processor "manifest" {
    output = "manifest.json"
  }
}
