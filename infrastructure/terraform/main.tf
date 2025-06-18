terraform {
  required_version = ">= 1.8.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.13"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = "~> 1.14"
    }
  }
  
  backend "s3" {
    bucket         = "xfinity-ai-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "xfinity-ai"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = var.vpc_cidr

  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets

  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${var.project_name}-cluster"
  cluster_version = var.kubernetes_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Cluster endpoint configuration
  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access_cidrs = var.allowed_cidrs

  # Cluster addons with latest versions
  cluster_addons = {
    coredns = {
      version = "v1.11.1-eksbuild.4"
      configuration_values = jsonencode({
        tolerations = [{
          operator = "Exists"
          effect   = "NoSchedule"
        }]
      })
    }
    kube-proxy = {
      version = "v1.29.0-eksbuild.1"
    }
    vpc-cni = {
      version = "v1.16.0-eksbuild.1"
      configuration_values = jsonencode({
        env = {
          ENABLE_PREFIX_DELEGATION = "true"
          WARM_PREFIX_TARGET       = "1"
        }
      })
    }
    aws-ebs-csi-driver = {
      version = "v1.28.0-eksbuild.1"
      service_account_role_arn = module.ebs_csi_irsa.iam_role_arn
    }
  }

  # Node groups configuration
  eks_managed_node_groups = {
    general = {
      name = "${var.project_name}-general"
      
      instance_types = ["m6i.large", "m6i.xlarge"]
      capacity_type  = "ON_DEMAND"
      
      min_size     = 3
      max_size     = 20
      desired_size = 5

      ami_type = "AL2_x86_64"
      
      vpc_security_group_ids = [aws_security_group.node_group.id]
      
      # Launch template configuration
      create_launch_template = true
      launch_template_name   = "${var.project_name}-general"
      launch_template_description = "Launch template for ${var.project_name} general node group"
      
      update_config = {
        max_unavailable_percentage = 25
      }
      
      labels = {
        role = "general"
      }
      
      taints = []
      
      # Node group networking
      subnet_ids = module.vpc.private_subnets
      
      # Instance refresh settings
      instance_refresh = {
        strategy = "Rolling"
        preferences = {
          min_healthy_percentage = 66
        }
      }
    }
    
    ai_workloads = {
      name = "${var.project_name}-ai"
      
      instance_types = ["c6i.2xlarge", "c6i.4xlarge"]
      capacity_type  = "SPOT"
      
      min_size     = 0
      max_size     = 10
      desired_size = 2
      
      ami_type = "AL2_x86_64"
      
      vpc_security_group_ids = [aws_security_group.node_group.id]
      
      labels = {
        role = "ai-workloads"
        workload = "compute-intensive"
      }
      
      taints = [{
        key    = "ai-workload"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
      
      subnet_ids = module.vpc.private_subnets
    }
  }

  # Cluster access configuration
  access_entries = {
    admin = {
      kubernetes_groups = ["system:masters"]
      principal_arn     = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      
      policy_associations = {
        admin = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = {
            type = "cluster"
          }
        }
      }
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Security Groups
resource "aws_security_group" "node_group" {
  name        = "${var.project_name}-node-group"
  description = "Security group for EKS node group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port = 443
    to_port   = 443
    protocol  = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-node-group"
  }
}

# RDS PostgreSQL
module "rds" {
  source = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "${var.project_name}-postgres"

  engine               = "postgres"
  engine_version       = "16.1"
  family               = "postgres16"
  major_engine_version = "16"
  instance_class       = "db.r6g.large"

  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_encrypted     = true

  db_name  = "xfinity_ai"
  username = "postgres"
  port     = 5432

  multi_az               = true
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [aws_security_group.rds.id]

  maintenance_window      = "Mon:00:00-Mon:03:00"
  backup_window          = "03:00-06:00"
  backup_retention_period = 30

  monitoring_interval    = 60
  monitoring_role_name   = "${var.project_name}-rds-monitoring"
  create_monitoring_role = true

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  create_cloudwatch_log_group     = true

  skip_final_snapshot = false
  deletion_protection = true

  performance_insights_enabled = true
  performance_insights_retention_period = 7

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.node_group.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds"
  }
}

# ElastiCache Redis
module "redis" {
  source = "terraform-aws-modules/elasticache/aws"
  version = "~> 1.0"

  replication_group_id       = "${var.project_name}-redis"
  description               = "Redis cluster for ${var.project_name}"

  node_type                 = "cache.r6g.large"
  port                      = 6379
  parameter_group_name      = "default.redis7"

  num_cache_clusters        = 2
  preferred_cache_cluster_azs = slice(data.aws_availability_zones.available.names, 0, 2)

  subnet_group_name = module.vpc.elasticache_subnet_group_name
  security_group_ids = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = random_password.redis_auth.result

  snapshot_retention_limit = 5
  snapshot_window         = "03:00-05:00"

  tags = {
    Environment = var.project_name
    Project     = var.project_name
  }
}

resource "random_password" "redis_auth" {
  length  = 32
  special = true
}

resource "aws_security_group" "redis" {
  name        = "${var.project_name}-redis"
  description = "Security group for ElastiCache Redis"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.node_group.id]
  }

  tags = {
    Name = "${var.project_name}-redis"
  }
}

# IAM role for EBS CSI driver
module "ebs_csi_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name             = "${var.project_name}-ebs-csi"
  attach_ebs_csi_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:ebs-csi-controller-sa"]
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Load Balancer Controller
module "load_balancer_controller_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name                              = "${var.project_name}-load-balancer-controller"
  attach_load_balancer_controller_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

data "aws_caller_identity" "current" {}
