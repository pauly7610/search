# Network Infrastructure Outputs
output "vpc_id" {
  description = "ID of the VPC created for the application"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs"
  value       = aws_nat_gateway.main[*].id
}

# Security Group Outputs
output "alb_security_group_id" {
  description = "Security group ID for the Application Load Balancer"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "Security group ID for application instances"
  value       = aws_security_group.app.id
}

output "rds_security_group_id" {
  description = "Security group ID for RDS database"
  value       = aws_security_group.rds.id
}

output "redis_security_group_id" {
  description = "Security group ID for Redis cache"
  value       = aws_security_group.redis.id
}

# Load Balancer Outputs
output "load_balancer_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

output "load_balancer_dns_name" {
  description = "DNS name of the load balancer for accessing the application"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "Canonical hosted zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "load_balancer_url" {
  description = "Full URL to access the application"
  value       = "http://${aws_lb.main.dns_name}"
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = aws_lb_target_group.app.arn
}

# Auto Scaling Group Outputs
output "autoscaling_group_name" {
  description = "Name of the Auto Scaling Group"
  value       = aws_autoscaling_group.app.name
}

output "autoscaling_group_arn" {
  description = "ARN of the Auto Scaling Group"
  value       = aws_autoscaling_group.app.arn
}

output "launch_template_id" {
  description = "ID of the launch template"
  value       = aws_launch_template.app.id
}

output "launch_template_latest_version" {
  description = "Latest version of the launch template"
  value       = aws_launch_template.app.latest_version
}

# AMI Information
output "ami_id" {
  description = "AMI ID used for launching instances"
  value       = data.aws_ami.xfinity_agent.id
}

output "ami_name" {
  description = "Name of the AMI used for instances"
  value       = data.aws_ami.xfinity_agent.name
}

output "ami_creation_date" {
  description = "Creation date of the AMI"
  value       = data.aws_ami.xfinity_agent.creation_date
}

# Database Outputs (Sensitive)
output "database_endpoint" {
  description = "RDS PostgreSQL endpoint for database connections"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_port" {
  description = "Port on which the database accepts connections"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "Name of the database"
  value       = aws_db_instance.main.db_name
}

output "database_username" {
  description = "Master username for the database"
  value       = aws_db_instance.main.username
  sensitive   = true
}

output "database_arn" {
  description = "ARN of the RDS instance"
  value       = aws_db_instance.main.arn
}

output "database_availability_zone" {
  description = "Availability zone of the RDS instance"
  value       = aws_db_instance.main.availability_zone
}

# Redis Cache Outputs
output "redis_endpoint" {
  description = "ElastiCache Redis endpoint for caching connections"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
}

output "redis_port" {
  description = "Port on which Redis accepts connections"
  value       = aws_elasticache_cluster.main.cache_nodes[0].port
}

output "redis_cluster_id" {
  description = "ID of the Redis cluster"
  value       = aws_elasticache_cluster.main.cluster_id
}

# Monitoring and Logging
output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group for application logs"
  value       = aws_cloudwatch_log_group.app_logs.name
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.app_logs.arn
}

# IAM Outputs
output "rds_monitoring_role_arn" {
  description = "ARN of the IAM role for RDS monitoring"
  value       = aws_iam_role.rds_monitoring.arn
}

# Connection Strings and URLs
output "database_connection_string" {
  description = "PostgreSQL connection string for the application"
  value       = "postgresql://${aws_db_instance.main.username}:${var.db_password}@${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}"
  sensitive   = true
}

output "redis_connection_string" {
  description = "Redis connection string for the application"
  value       = "redis://${aws_elasticache_cluster.main.cache_nodes[0].address}:${aws_elasticache_cluster.main.cache_nodes[0].port}"
}

# Application Configuration for Environment Variables
output "application_environment_variables" {
  description = "Environment variables for application configuration"
  value = {
    DATABASE_URL     = "postgresql://${aws_db_instance.main.username}:${var.db_password}@${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}"
    REDIS_URL        = "redis://${aws_elasticache_cluster.main.cache_nodes[0].address}:${aws_elasticache_cluster.main.cache_nodes[0].port}"
    AWS_REGION       = var.aws_region
    ENVIRONMENT      = var.environment
    LOG_GROUP_NAME   = aws_cloudwatch_log_group.app_logs.name
  }
  sensitive = true
}

# Resource Counts
output "resource_summary" {
  description = "Summary of created resources"
  value = {
    vpc_count              = 1
    public_subnets         = length(aws_subnet.public)
    private_subnets        = length(aws_subnet.private)
    security_groups        = 4
    nat_gateways          = length(aws_nat_gateway.main)
    load_balancers        = 1
    rds_instances         = 1
    redis_clusters        = 1
    autoscaling_groups    = 1
  }
}

# Cost Optimization Information
output "instance_information" {
  description = "Information about EC2 instances for cost tracking"
  value = {
    instance_type        = var.instance_type
    min_capacity         = var.min_size
    max_capacity         = var.max_size
    desired_capacity     = var.desired_capacity
    database_class       = var.db_instance_class
    redis_node_type      = aws_elasticache_cluster.main.node_type
  }
}

# DNS and SSL Information (if applicable)
output "dns_configuration" {
  description = "DNS configuration information"
  value = {
    load_balancer_dns    = aws_lb.main.dns_name
    load_balancer_zone_id = aws_lb.main.zone_id
    domain_name          = var.domain_name != "" ? var.domain_name : "Not configured"
    certificate_arn      = var.certificate_arn != "" ? var.certificate_arn : "Not configured"
  }
}

# Deployment Information
output "deployment_information" {
  description = "Information about the deployment for documentation"
  value = {
    project_name       = var.project_name
    environment        = var.environment
    aws_region         = var.aws_region
    deployment_time    = timestamp()
    terraform_version  = "~> 1.5.0"
  }
}
