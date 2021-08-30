/*
 * Simple VPC allowing subnets in multiple availability zones.
 */

locals {
  /*
   * Assigning cidrsubet netnum via a lookup provides stability if zones are added or removed.
   */
  availability_zones_cidrsubnet_netnum_lookup = {
    "1a" = 0,
    "1b" = 1,
    "1c" = 2,
    "1d" = 3,
    "1e" = 4,
    "1f" = 5,
    "1g" = 6,
    "1h" = 7,
    "1i" = 8,
  }

  /*
   * Use var.availability_zone as default output for subnet_id if provided, otherwise choose a default.
   */
  resolved_availability_zone = ( var.availability_zone != null ?
                                 var.availability_zone :
                                 coalesce(var.availability_zones...)
                               )

  /*
   * Ensure var.availability_zone is contained in var.availability_zones.
   */
  resolved_availability_zones = ( var.availability_zone != null ?
                                  setunion([var.availability_zone], var.availability_zones) :
                                  var.availability_zones
                                )
}

/*
 * The VPC.
 */
resource "aws_vpc" "vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = local.module_tags
}

/*
 * Subnet for each availability zone.
 */
resource "aws_subnet" "subnet" {
  for_each = local.resolved_availability_zones

  availability_zone = each.value
  cidr_block        = cidrsubnet(
                        aws_vpc.vpc.cidr_block,
                        8,
                        # For brevity, assumes availability zones all have two hyphens in format xxx-xxx-xxx
                        local.availability_zones_cidrsubnet_netnum_lookup[split("-",each.value)[2]]
                      )

  vpc_id            = aws_vpc.vpc.id

  map_public_ip_on_launch = var.map_public_ip_on_launch

  tags = local.module_tags
}

/*
 * The Internet Gateway.
 */
resource "aws_internet_gateway" "gateway" {
  vpc_id = aws_vpc.vpc.id

  tags = local.module_tags
}

/*
 * A route out through the Gateway.
 */
resource "aws_route_table" "route" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gateway.id
  }

  tags = local.module_tags
}

/*
 * Associate the route with each subnet.
 */
resource "aws_route_table_association" "route" {
  for_each = var.availability_zones
  subnet_id      = aws_subnet.subnet[each.value].id

  route_table_id = aws_route_table.route.id
}
