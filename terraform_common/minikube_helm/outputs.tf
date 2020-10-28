/*
 * Public IP of the instance.
 */
output "ip" {
  value = aws_instance.minikube.public_ip
}

output "identity_file" {
  value = local_file.instance_key_private.filename
}
