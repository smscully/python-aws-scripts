output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.vpc.id
}

output "instance_ip" {
  description = "IP address of the instance"
  value       = aws_instance.instance.public_ip
}
