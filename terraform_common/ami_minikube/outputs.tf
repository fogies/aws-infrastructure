/*
 * ID of the AMI.
 */
output "id" {
  value = data.aws_ami.minikube.id
}
