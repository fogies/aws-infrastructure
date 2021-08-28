/*
 * If we were not provided an elastic IP, create our own.
 */
resource "aws_eip" "eip" {
  count = var.eip_id != null ? 0 : 1
}

/*
 * Resolve our elastic IP, either as provided or created.
 */
locals {
  resolved_eip_id = var.eip_id != null ? var.eip_id : aws_eip.eip[0].id
  resolved_public_ip = var.eip_id != null ? var.eip_public_ip : aws_eip.eip[0].public_ip
}

/*
 * Associate to our elastic IP.
 */
resource "aws_eip_association" "eip_association" {
  instance_id = aws_instance.minikube.id
  allocation_id = local.resolved_eip_id
}
