/*
 * ID of the VPC.
 */
output "vpc_id" {
  value = aws_vpc.vpc.id
}

/*
 * ID of the default security group, automatically assigned by AWS.
 */
output "default_security_group_id" {
  value = aws_vpc.vpc.default_security_group_id
}

/*
 * ID of a default subnet.
 */
output "subnet_id" {
  value = aws_subnet.subnet[local.resolved_availability_zone].id
}

/*
 * List of IDs of all subnets.
 */
output "subnet_ids" {
  value = [ for availability_zone in local.resolved_availability_zones : aws_subnet.subnet[availability_zone].id ]
}

/*
 * Map from availability zones to subnet IDs.
 */
output "availability_zone_subnet_ids" {
  value = {
    for availability_zone in local.resolved_availability_zones :
    availability_zone => aws_subnet.subnet[availability_zone].id
  }
}
