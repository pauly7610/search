variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region for AMI building"
}

variable "instance_type" {
  type        = string
  default     = "t3.medium"
  description = "Instance type for building AMI"
}

variable "source_ami_filter" {
  type = string
  default = "ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"
  description = "Source AMI filter pattern"
}

packer {
  required_plugins {
    amazon = {
      version = ">= 1.2.8"
      source  = "github.com/hashicorp/amazon"
    }
    ansible = {
      version = ">= 1.1.0"
      source = "github.com/hashicorp/ansible"
    }
  }
}

source "amazon-ebs" "xfinity_agent" {
  ami_name      = "xfinity-agent-${formatdate("YYYYMMDD-HHmmss", timestamp())}"
  instance_type = var.instance_type
  region        = var.aws_region
  
  source_ami_filter {
    filters = {
      name                = var.source_ami_filter
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    owners      = ["099720109477"] # Canonical Ubuntu
    most_recent = true
  }
  
  ssh_username = "ubuntu"
  
  # Security group for Packer build
  temporary_security_group_source_cidrs = ["0.0.0.0/0"]
  
  # EBS configuration
  ebs_optimized = true
  
  root_block_device {
    volume_type = "gp3"
    volume_size = 50
    encrypted   = true
    delete_on_termination = true
  }
  
  tags = {
    Name        = "XfinityAgentAMI"
    Service     = "CustomerSupport"
    Environment = "Production"
    BuildDate   = "{{ timestamp }}"
    Application = "XfinityAI"
  }
}

build {
  name = "xfinity-agent-build"
  sources = ["source.amazon-ebs.xfinity_agent"]

  # Wait for cloud-init to complete
  provisioner "shell" {
    inline = [
      "echo 'Waiting for cloud-init to complete...'",
      "cloud-init status --wait",
      "echo 'Cloud-init completed successfully'"
    ]
  }

  # Run Ansible playbook
  provisioner "ansible" {
    playbook_file = "./ansible/playbook_bake_image.yml"
    user         = "ubuntu"
    
    extra_arguments = [
      "--extra-vars",
      "ansible_python_interpreter=/usr/bin/python3"
    ]
    
    ansible_env_vars = [
      "ANSIBLE_HOST_KEY_CHECKING=False",
      "ANSIBLE_SSH_ARGS='-o ForwardAgent=yes -o ControlMaster=auto -o ControlPersist=60s'",
      "ANSIBLE_NOCOLOR=True"
    ]
  }

  # Create manifest for Terraform
  post-processor "manifest" {
    output = "manifest.json"
    strip_path = true
    custom_data = {
      build_time = "{{ timestamp }}"
      build_user = "{{ user `USER` }}"
    }
  }
}
