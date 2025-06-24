#!/bin/bash

set -e

# Configuration
PROJECT_NAME="xfinity-ai"
ENVIRONMENT=${1:-production}
CLOUDS=${2:-"aws,azure,gcp"}
DB_PASSWORD=${3:-$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)}
SECRET_KEY=${4:-$(openssl rand -base64 32)}

echo "🚀 Deploying ${PROJECT_NAME} to multi-cloud environment: ${ENVIRONMENT}"
echo "☁️  Target clouds: ${CLOUDS}"

# Function to validate prerequisites
validate_prerequisites() {
    echo "🔍 Validating prerequisites..."
    
    # Check if required tools are installed
    command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform is required but not installed."; exit 1; }
    command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl is required but not installed."; exit 1; }
    command -v helm >/dev/null 2>&1 || { echo "❌ Helm is required but not installed."; exit 1; }
    command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }
    
    echo "✅ Prerequisites validated"
}

# Function to build and push container images
build_and_push_images() {
    local cloud=$1
    echo "🐳 Building and pushing container images for ${cloud}..."
    
    case $cloud in
        "aws")
            # Build and push to ECR
            aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com
            
            # Backend
            docker build -t ${PROJECT_NAME}/backend:${ENVIRONMENT} ./backend
            docker tag ${PROJECT_NAME}/backend:${ENVIRONMENT} ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/${PROJECT_NAME}/backend:${ENVIRONMENT}
            docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/${PROJECT_NAME}/backend:${ENVIRONMENT}
            
            # Frontend  
            docker build -t ${PROJECT_NAME}/frontend:${ENVIRONMENT} ./frontend
            docker tag ${PROJECT_NAME}/frontend:${ENVIRONMENT} ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/${PROJECT_NAME}/frontend:${ENVIRONMENT}
            docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/${PROJECT_NAME}/frontend:${ENVIRONMENT}
            ;;
        "azure")
            # Build and push to ACR
            az acr login --name ${PROJECT_NAME}acr${ENVIRONMENT}
            
            # Backend
            docker build -t ${PROJECT_NAME}/backend:${ENVIRONMENT} ./backend
            docker tag ${PROJECT_NAME}/backend:${ENVIRONMENT} ${PROJECT_NAME}acr${ENVIRONMENT}.azurecr.io/${PROJECT_NAME}/backend:${ENVIRONMENT}
            docker push ${PROJECT_NAME}acr${ENVIRONMENT}.azurecr.io/${PROJECT_NAME}/backend:${ENVIRONMENT}
            
            # Frontend
            docker build -t ${PROJECT_NAME}/frontend:${ENVIRONMENT} ./frontend  
            docker tag ${PROJECT_NAME}/frontend:${ENVIRONMENT} ${PROJECT_NAME}acr${ENVIRONMENT}.azurecr.io/${PROJECT_NAME}/frontend:${ENVIRONMENT}
            docker push ${PROJECT_NAME}acr${ENVIRONMENT}.azurecr.io/${PROJECT_NAME}/frontend:${ENVIRONMENT}
            ;;
        "gcp")
            # Build and push to Artifact Registry
            gcloud auth configure-docker us-central1-docker.pkg.dev
            
            # Backend
            docker build -t ${PROJECT_NAME}/backend:${ENVIRONMENT} ./backend
            docker tag ${PROJECT_NAME}/backend:${ENVIRONMENT} us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/${PROJECT_NAME}-${ENVIRONMENT}/${PROJECT_NAME}/backend:${ENVIRONMENT}
            docker push us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/${PROJECT_NAME}-${ENVIRONMENT}/${PROJECT_NAME}/backend:${ENVIRONMENT}
            
            # Frontend
            docker build -t ${PROJECT_NAME}/frontend:${ENVIRONMENT} ./frontend
            docker tag ${PROJECT_NAME}/frontend:${ENVIRONMENT} us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/${PROJECT_NAME}-${ENVIRONMENT}/${PROJECT_NAME}/frontend:${ENVIRONMENT}
            docker push us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/${PROJECT_NAME}-${ENVIRONMENT}/${PROJECT_NAME}/frontend:${ENVIRONMENT}
            ;;
    esac
    
    echo "✅ Images built and pushed for ${cloud}"
}

# Function to deploy infrastructure
deploy_infrastructure() {
    local cloud=$1
    echo "🏗️  Deploying infrastructure for ${cloud}..."
    
    cd infrastructure/terraform/${cloud}
    
    # Initialize Terraform
    terraform init
    
    # Create terraform.tfvars with your specific values
    cat > terraform.tfvars <<EOF
project_name = "${PROJECT_NAME}"
environment = "${ENVIRONMENT}"
db_password = "${DB_PASSWORD}"
EOF
    
    # Add cloud-specific variables
    case $cloud in
        "aws")
            cat >> terraform.tfvars <<EOF
region = "us-west-2"
kubernetes_version = "1.28"
node_count = 3
instance_type = "t3.medium"
db_instance_class = "db.t3.micro"
db_allocated_storage = 20
db_max_allocated_storage = 100
redis_node_type = "cache.t3.micro"
EOF
            ;;
        "azure")
            cat >> terraform.tfvars <<EOF
location = "East US"
kubernetes_version = "1.28"
node_count = 3
node_size = "Standard_D2s_v3"
db_storage_mb = 32768
db_sku_name = "GP_Standard_D2s_v3"
redis_capacity = 1
redis_family = "C"
redis_sku_name = "Standard"
EOF
            ;;
        "gcp")
            cat >> terraform.tfvars <<EOF
project_id = "${GCP_PROJECT_ID}"
region = "us-central1"
zone = "us-central1-a"
node_count = 3
machine_type = "e2-medium"
db_tier = "db-f1-micro"
redis_tier = "STANDARD_HA"
redis_memory_size_gb = 1
EOF
            ;;
    esac
    
    # Plan and apply
    terraform plan -var-file="terraform.tfvars"
    terraform apply -auto-approve -var-file="terraform.tfvars"
    
    cd ../../..
    echo "✅ Infrastructure deployed for ${cloud}"
}

# Function to run database migrations
run_migrations() {
    local cloud=$1
    echo "🗄️  Running database migrations for ${cloud}..."
    
    # Get database connection details from Terraform output
    cd infrastructure/terraform/${cloud}
    
    case $cloud in
        "aws")
            DB_HOST=$(terraform output -raw postgres_endpoint)
            ;;
        "azure")
            DB_HOST=$(terraform output -raw postgres_fqdn)
            ;;
        "gcp")
            DB_HOST=$(terraform output -raw postgres_private_ip)
            ;;
    esac
    
    cd ../../..
    
    # Create temporary .env for migrations
    cat > backend/src/.env.migration <<EOF
SECRET_KEY="${SECRET_KEY}"
DATABASE_URL="postgresql+asyncpg://xfinity_admin:${DB_PASSWORD}@${DB_HOST}:5432/xfinity_ai"
ENVIRONMENT="${ENVIRONMENT}"
EOF
    
    # Run migrations using the temporary env file
    cd backend
    PYTHONPATH=. python -c "
import os
os.environ['PYDANTIC_SETTINGS_FILE'] = 'src/.env.migration'
from src.config.settings import settings
print(f'Using database: {settings.DATABASE_URL}')
"
    
    # Run Alembic migrations
    PYTHONPATH=. python -m alembic upgrade head
    
    # Clean up
    rm src/.env.migration
    cd ..
    
    echo "✅ Database migrations completed for ${cloud}"
}

# Function to deploy Kubernetes applications
deploy_kubernetes() {
    local cloud=$1
    echo "☸️  Deploying Kubernetes applications for ${cloud}..."
    
    # Set kubectl context
    case $cloud in
        "aws")
            aws eks update-kubeconfig --region us-west-2 --name ${PROJECT_NAME}-eks-${ENVIRONMENT}
            CONTEXT="arn:aws:eks:us-west-2:${AWS_ACCOUNT_ID}:cluster/${PROJECT_NAME}-eks-${ENVIRONMENT}"
            ;;
        "azure")
            az aks get-credentials --resource-group ${PROJECT_NAME}-${ENVIRONMENT} --name ${PROJECT_NAME}-aks-${ENVIRONMENT} --overwrite-existing
            CONTEXT="${PROJECT_NAME}-aks-${ENVIRONMENT}"
            ;;
        "gcp")
            gcloud container clusters get-credentials ${PROJECT_NAME}-gke-${ENVIRONMENT} --region us-central1 --project ${GCP_PROJECT_ID}
            CONTEXT="gke_${GCP_PROJECT_ID}_us-central1_${PROJECT_NAME}-gke-${ENVIRONMENT}"
            ;;
    esac
    
    # Create namespace
    kubectl create namespace xfinity-ai --dry-run=client -o yaml | kubectl apply -f -
    
    # Create secrets
    kubectl create secret generic ${PROJECT_NAME}-secrets \
        --from-literal=secret-key="${SECRET_KEY}" \
        --from-literal=database-url="postgresql+asyncpg://xfinity_admin:${DB_PASSWORD}@${DB_HOST}:5432/xfinity_ai" \
        --from-literal=redis-url="${REDIS_URL}" \
        --from-literal=openai-api-key="${OPENAI_API_KEY:-}" \
        --namespace=xfinity-ai \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy using Helm
    helm upgrade --install ${PROJECT_NAME}-${cloud} \
        ./infrastructure/helm/xfinity-ai \
        --namespace=xfinity-ai \
        --values=./infrastructure/k8s/values-common.yaml \
        --values=./infrastructure/k8s/values-${cloud}.yaml \
        --set global.environment=${ENVIRONMENT} \
        --set global.cloud=${cloud}
    
    echo "✅ Kubernetes applications deployed for ${cloud}"
}

# Function to verify deployment
verify_deployment() {
    local cloud=$1
    echo "🔍 Verifying deployment for ${cloud}..."
    
    # Check pod status
    kubectl get pods -n xfinity-ai -l cloud=${cloud}
    
    # Check services
    kubectl get services -n xfinity-ai -l cloud=${cloud}
    
    # Check ingress
    kubectl get ingress -n xfinity-ai
    
    echo "✅ Deployment verified for ${cloud}"
}

# Main deployment logic
main() {
    validate_prerequisites
    
    IFS=',' read -ra CLOUD_ARRAY <<< "$CLOUDS"
    
    for cloud in "${CLOUD_ARRAY[@]}"; do
        echo ""
        echo "🌟 Starting deployment for ${cloud}..."
        
        case $cloud in
            "aws"|"azure"|"gcp")
                build_and_push_images $cloud
                deploy_infrastructure $cloud
                run_migrations $cloud
                deploy_kubernetes $cloud
                verify_deployment $cloud
                ;;
            *)
                echo "❌ Unsupported cloud: $cloud"
                exit 1
                ;;
        esac
        
        echo "✅ Deployment completed for ${cloud}"
    done
    
    echo ""
    echo "🎉 Multi-cloud deployment completed successfully!"
    echo "📊 Database password: ${DB_PASSWORD}"
    echo "🔑 Secret key: ${SECRET_KEY}"
    echo ""
    echo "🌐 Access your applications:"
    for cloud in "${CLOUD_ARRAY[@]}"; do
        echo "   ${cloud}: https://app-${cloud}.xfinity-ai.com"
    done
}

# Run main function
main 