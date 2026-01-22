# 생성된 값 확인용 output

output "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.main.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS of the main EC2 instance"
  value       = aws_instance.main.public_dns
}