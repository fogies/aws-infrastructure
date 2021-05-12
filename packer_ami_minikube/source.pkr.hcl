/*
 * Configuration of the AWS context and source AMI.
 */
source "amazon-ebs" "minikube" {
  # Name of the output AMI
  ami_name = var.build_ami_name

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
    # This will be replaced with an NVMe name
    # - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/device_naming.html
    # - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/nvme-ebs-volumes.html
    #
    # For future robustness, can access AWS Volume ID with:
    # - lsblk -o +SERIAL
    # - Would probably need to move creation of the device into a provisioner
    device_name = "/dev/sdf"

    volume_size = 10
    volume_type = "gp3"
    iops = 3000
    delete_on_termination = true
  }

  # Configured over SSH
  communicator = "ssh"
  ssh_username = "ubuntu"

  # Build in a VPC and Subnet provided as variables
  vpc_id = var.vpc_packer_vpc_id
  subnet_id = var.vpc_packer_subnet_id
}
