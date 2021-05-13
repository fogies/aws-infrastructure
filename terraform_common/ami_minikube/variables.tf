variable "configuration" {
  # Desired configuration of the AMI.
  #
  # Valid values are:
  # - "amd64-medium": Designed for t3.medium, amd64 with 2g of available memory
  # - "amd64-large": Designed for t3.large, amd64 with 6g of available memory

  type = string
}
