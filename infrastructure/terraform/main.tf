terraform {
  required_providers {
    random = {
      source = "hashicorp/random"
    }
  }
}

provider "random" {}

resource "random_pet" "project" {}

# Placeholder for cloud resources (VPC, DB, etc.)
# Adapt for your cloud provider (AWS, GCP, Azure)
# Example: AWS RDS, EC2, S3, etc. 