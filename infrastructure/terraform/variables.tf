# AWS Configuration
variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# Project Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "xfinity-agent"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}

# EC2 Configuration
variable "instance_type" {
  description = "EC2 instance type for application servers"
  type        = string
  default     = "t3.medium"
}

variable "key_pair_name" {
  description = "Name of AWS key pair for EC2 access"
  type        = string
  default     = ""
}

variable "min_size" {
  description = "Minimum number of instances in Auto Scaling Group"
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum number of instances in Auto Scaling Group"
  type        = number
  default     = 6
}

variable "desired_capacity" {
  description = "Desired number of instances in Auto Scaling Group"
  type        = number
  default     = 2
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "xfinity_agent"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "xfinity_admin"
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

# Application Configuration
variable "openai_api_key" {
  description = "OpenAI API key for LLM services"
  type        = string
  sensitive   = true
}

variable "sentry_dsn" {
  description = "Sentry DSN for error monitoring"
  type        = string
  sensitive   = true
  default     = ""
}

# Load Balancer Configuration  
variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

# Monitoring Configuration
variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring and alerting"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 30
}

# Tags
variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "XfinityAgent"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
