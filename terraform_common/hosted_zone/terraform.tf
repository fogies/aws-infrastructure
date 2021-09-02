/*
 * Zone for managing our DNS.
 */
resource "aws_route53_zone" "zone" {
  name = var.name

  tags = local.module_tags
}

/*
 * Whenever the zone is created, or its name servers are otherwise modified,
 * update the domain to point and the name servers for the zone.
 *
 * https://github.com/hashicorp/terraform-provider-aws/issues/88
 */
resource "null_resource" "zone_nameservers" {
  triggers = {
    nameservers = join(", ",sort(aws_route53_zone.zone.name_servers))
  }

  provisioner "local-exec" {
    command = "aws route53domains update-domain-nameservers --domain-name ${var.name} --nameservers ${join(" ",formatlist(" Name=%s",sort(aws_route53_zone.zone.name_servers)))}"
  }
}

/*
 * Format the address records for use in a for_each.
 */
locals {
  resolved_address_records = zipmap(
    [ for record_current in var.address_records : record_current.name ],
    var.address_records
  )
}

/*
 * Address records in the zone.
 */
resource "aws_route53_record" "address_records" {
  for_each = local.resolved_address_records

  zone_id = aws_route53_zone.zone.zone_id

  type = "A"
  ttl = "60"

  name = each.value.name
  records = [each.value.ip]
}
