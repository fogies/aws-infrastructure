/*
 * Resolve our elastic IP, either as provided or created.
 */
locals {
  resolved_public_ip = var.create_eip ? one(aws_eip.eip).public_ip : var.eip_public_ip
}

/*
 * If we were not provided an elastic IP, create our own.
 */
resource "aws_eip" "eip" {
  count = var.create_eip ? 1 : 0

  tags = local.module_tags
}

/*
 * Associate to our elastic IP.
 */
resource "aws_eip_association" "eip_association" {
  instance_id = aws_instance.minikube.id
  allocation_id = var.create_eip ? one(aws_eip.eip).id : var.eip_id
}
