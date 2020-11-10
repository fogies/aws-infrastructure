/*
 * ID of the VPC.
 */
output "vpc_id" {
  value = aws_vpc.vpc.id
}

/*
 * ID of the subnet.
 */
output "subnet_id" {
  value = aws_subnet.subnet.id
}
