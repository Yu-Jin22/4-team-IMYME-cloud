variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-2"
}

variable "environment" {
  description = "Environment name (dev, release, prod)"
  type        = string
  default     = "release"
}

variable "parameters" {
  description = "Map of SSM parameters to create"
  type = map(object({
    value       = string
    type        = string
    description = string
    tier        = optional(string, "Standard")
  }))
}
