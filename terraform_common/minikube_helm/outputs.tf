/*
 * ID of the instance.
 */
output "id" {
  value = aws_instance.minikube.id
}

/*
 * Public IP of the instance.
 */
output "ip" {
  value = aws_instance.minikube.public_ip
}

/*
 * Path to an identify file for SSH access.
 */
output "identity_file" {
  value = local_file.instance_key_private.filename
}
