# Our AWS Source
source "amazon-ebs" "ubuntu-minikube" {
  # Name of the output AMI
  ami_name = "ami-minikube-{{timestamp}}"
  
  # Build in US East 1 with a t3.medium
  region = "us-east-1"
  instance_type = "t3.medium"
  
  # Build from a recent Ubuntu 20 image
  source_ami_filter {
    filters = {
      name =  "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"
	  # name = "ubuntu-minimal/images/hvm-ssd/ubuntu-focal-20.04-amd64-minimal-*"
    }
    owners = ["099720109477"]
    most_recent = true
  }
  
  # Configured over SSH using temporary credentials
  communicator = "ssh"
  ssh_username = "ubuntu"
  
  # Build in VPC and Subnet provided as variables
  vpc_id = var.packernetwork_vpc_id
  subnet_id = var.packernetwork_subnet_id
}

# Build on that source
build {
  sources = [
    "source.amazon-ebs.ubuntu-minikube"
  ]

  # Apply any updates
  provisioner "shell" {
    inline = [
      "sudo apt-get --quiet --assume-yes update",
      "sudo apt-get --quiet --assume-yes upgrade",
	]
	
	# Allow retries because of apt state errors
	max_retries = 5
  }
  
  # Install Ansible, available as a package in Ubuntu 20
  provisioner "shell" {
    inline = [
      "sudo apt-get --quiet --assume-yes update",
      "sudo apt-get --quiet --assume-yes install ansible",
	]

	# Allow retries because of apt state errors
	max_retries = 5
  }

  # Install Docker
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_docker.yml"
  }

  # Reboot to apply group permissions for non-sudo Docker access
  provisioner "shell" {
    inline = [
	  "sudo reboot",
	]
	
	# Expect a potential disconnect because of the reboot
	expect_disconnect = true
  }

  # Confirm non-sudo Docker access
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_docker_confirm.yml"
	
	# Pause and retries to allow for reboot
	pause_before = "5s"
	max_retries = 10
  }

  # Install Minikube
  provisioner "ansible-local" {
    playbook_file = "../ansible/ansible_minikube.yml"
  }

  # Output manifest for recovering resulting AMI
  post-processor "manifest" {
    output = "manifest.json"
  }
}

