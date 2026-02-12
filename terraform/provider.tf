terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend configuration (optional - uncomment if using remote backend)
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "parameter-store/terraform.tfstate"
  #   region         = "ap-northeast-2"
  #   encrypt        = true
  #   dynamodb_table = "terraform-lock"
  # }
}

provider "aws" {
  region  = var.aws_region
  profile = "halo"

  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = "IMYME"
    }
  }
}
