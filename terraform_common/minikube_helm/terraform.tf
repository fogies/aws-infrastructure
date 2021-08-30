/*
 * ID of the AMI we want.
 */
module "ami_minikube" {
  source = "../ami_minikube"

  configuration = var.ami_configuration
}

/*
 * Security groups for our instance.
 */
module "instance_security_groups" {
  source = "../security_groups"

  vpc_id = local.resolved_vpc_id

  allow_egress_to_anywhere = true
  allow_http_from_anywhere = true
  allow_ssh_from_anywhere  = true

  tags = local.module_tags
}

/*
 * The actual instance.
 */
resource "aws_instance" "minikube" {
  ami = module.ami_minikube.id
  instance_type = var.aws_instance_type

  subnet_id         = local.resolved_subnet_id
  vpc_security_group_ids = concat(
    [ local.resolved_vpc_default_security_group_id ],
    module.instance_security_groups.security_group_ids
  )

  key_name = aws_key_pair.instance_key_pair.id

  tags = local.module_tags
}
