/*
 * ID of the VPC.
 */
output "vpc_id" {
  value = aws_vpc.vpc.id
}

/*
 * ID of the default subnet.
 */
output "subnet_id" {
  value = aws_subnet.subnet[local.resolved_availability_zone].id
}

/*
 * ID of all the subnets.
 */
output "subnet_ids" {
  value = {
    for availability_zone in local.resolved_availability_zones :
    availability_zone => aws_subnet.subnet[availability_zone].id
  }
}
