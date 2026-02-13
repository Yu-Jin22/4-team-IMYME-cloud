resource "aws_ssm_parameter" "parameters" {
  for_each = var.parameters

  name        = "/MINE/MVP1/FE/ENV/${each.key}"
  description = each.value.description
  type        = each.value.type
  value       = each.value.value
  tier        = each.value.tier

  tags = {
    Name = each.key
  }
}
