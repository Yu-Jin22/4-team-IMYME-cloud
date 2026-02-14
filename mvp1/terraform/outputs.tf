output "parameter_arns" {
  description = "ARNs of all created parameters"
  value = {
    for k, v in aws_ssm_parameter.parameters : k => v.arn
  }
}

output "parameter_names" {
  description = "Names of all created parameters"
  value = {
    for k, v in aws_ssm_parameter.parameters : k => v.name
  }
}

output "target_group_arn" {
  description = "ARN of the backend target group"
  value       = aws_lb_target_group.be_prod.arn
}

output "target_group_name" {
  description = "Name of the backend target group"
  value       = aws_lb_target_group.be_prod.name
}
