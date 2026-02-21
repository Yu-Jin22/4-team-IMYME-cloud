resource "aws_ssm_parameter" "fe_parameters" {
  for_each = var.fe_parameters

  name        = "/MINE/MVP2/FE/ENV/${each.key}"
  description = each.value.description
  type        = each.value.type
  value       = each.value.value
  tier        = each.value.tier

  tags = {
    Name = each.key
  }
}
