/*
 * Configuration of the AMI.
 */
source "amazon-ebs" "minikube" {
  # Name of the output AMI
  ami_name = "ami-minikube-{{timestamp}}"
  
  # Configure AWS variables
  region = var.aws_region
  instance_type = var.aws_instance_type
  
  # Filter an image to use as the base of the build
  source_ami_filter {
    filters = {
      name = var.source_ami_filter_name
    }
    owners = var.source_ami_filter_owners
    most_recent = true
  }

  # Create an additional volume for Docker images and data
  launch_block_device_mappings {
    device_name = "/dev/sdf"
    volume_size = 10
    volume_type = "gp2"
    delete_on_termination = true
  }
  
  # Configured over SSH
  communicator = "ssh"
  ssh_username = "ubuntu"
  
  # Build in a VPC and Subnet provided as variables
  vpc_id = var.vpc_packer_vpc_id
  subnet_id = var.vpc_packer_subnet_id
}

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
	
	# Allow retries because of apt state errors
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

	# Allow retries because of apt state errors
	max_retries = 5
  }

  /*
   * Configure Volume for Docker Storage
   */
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_docker_volume.yml"

    # Disable color
    command = "PYTHONUNBUFFERED=1 ansible-playbook"
  }

  /*
   * Install Docker
   */
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_docker.yml"

    # Disable color
    command = "PYTHONUNBUFFERED=1 ansible-playbook"
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
    playbook_file = "../ansible/ansible_docker_confirm.yml"
	
    # Disable color
    command = "PYTHONUNBUFFERED=1 ansible-playbook"

	# Pause and retries to allow for reboot
	pause_before = "5s"
	max_retries = 10
  }

  /*
   * Install Minikube
   */
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_minikube.yml"

    # Disable color
    command = "PYTHONUNBUFFERED=1 ansible-playbook"
  }

  /*
   * Install Helm
   */
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_helm.yml"

    # Disable color
    command = "PYTHONUNBUFFERED=1 ansible-playbook"
  }

  /*
   * Output manifest for recovering resulting AMI
   */
  post-processor "manifest" {
    output = "manifest.json"
  }
}
