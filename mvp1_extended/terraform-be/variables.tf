variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "ap-northeast-2"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "parameters" {
  description = "Map of parameters to create in Parameter Store (Backend)"
  type = map(object({
    value       = string
    type        = string # String, StringList, or SecureString
    description = optional(string)
    tier        = optional(string, "Standard") # Standard or Advanced
  }))
  default = {}
}

variable "fe_parameters" {
  description = "Map of parameters to create in Parameter Store (Frontend)"
  type = map(object({
    value       = string
    type        = string # String, StringList, or SecureString
    description = optional(string)
    tier        = optional(string, "Standard") # Standard or Advanced
  }))
  default = {}
}
