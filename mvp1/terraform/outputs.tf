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

output "fe_target_group_arn" {
  description = "ARN of the frontend target group"
  value       = aws_lb_target_group.fe_prod.arn
}

output "fe_target_group_name" {
  description = "Name of the frontend target group"
  value       = aws_lb_target_group.fe_prod.name
}

output "be_asg_name" {
  description = "Name of the backend ASG"
  value       = aws_autoscaling_group.be_prod.name
}

output "fe_asg_name" {
  description = "Name of the frontend ASG"
  value       = aws_autoscaling_group.fe_prod.name
}
