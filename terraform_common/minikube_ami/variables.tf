variable "owner_id" {
  # ID of AWS account that owns the AMI.
  type = string
}

variable "instance_type" {
  # Instance type on which the AMI will be run.
  #
  # Valid values are:
  # - "t3.medium"
  # - "t3.large"

  type = string
  validation {
    condition = contains(["t3.medium", "t3.large"], var.instance_type)
    error_message = "Invalid or unsupported instance_type."
  }
}

variable "docker_volume_size" {
  # Size of associated docker volume.
  type = number
}

variable "build_timestamp" {
  # Timestamp associated with the build.
  type = string
}
