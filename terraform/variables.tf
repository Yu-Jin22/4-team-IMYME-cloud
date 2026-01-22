variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-2"
}

variable "availability_zone" {
  description = "AZ for the public subnet"
  type        = string
  default     = "ap-northeast-2a"
}

variable "project" {
  description = "Project name (used for naming/tags)"
  type        = string
  default     = "mine"
}

variable "env" {
  description = "Environment name (dev/prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Public subnet CIDR block"
  type        = string
  default     = "10.0.1.0/24"
}

variable "allowed_cidrs" {
  description = "CIDRs allowed to access inbound ports (dev default open)."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "egress_cidrs" {
  description = "CIDRs allowed for outbound traffic (dev default open)."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t4g.medium"
}

variable "key_name" {
  description = "Existing EC2 Key Pair name"
  type        = string
  default     = "mine"
}

variable "root_volume_size_gb" {
  description = "Root EBS volume size (GB)"
  type        = number
  default     = 30
}

variable "root_volume_type" {
  description = "Root EBS volume type"
  type        = string
  default     = "gp3"
}

variable "ubuntu_ami_name_pattern" {
  description = "Ubuntu AMI name pattern for lookup (ARM64)."
  type        = string
  default     = "ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-arm64-server-*"
}