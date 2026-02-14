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
