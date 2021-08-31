/*
 * ID of the Elastic IP.
 */
output "id" {
  value = aws_eip.eip.id
}

/*
 * Public IP of the Elastic IP.
 */
output "public_ip" {
  value = aws_eip.eip.public_ip
}
