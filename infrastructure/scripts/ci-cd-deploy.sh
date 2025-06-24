#!/bin/bash

set -e

# ================================
# ADVANCED CI/CD DEPLOYMENT SCRIPT
# ================================

# Configuration
PROJECT_NAME="xfinity-ai"
ENVIRONMENT=${1:-staging}
CLOUD=${2:-aws}
VERSION=${3:-$(git rev-parse --short HEAD)}
NAMESPACE=${4:-xfinity-ai}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validation function
validate_environment() {
    log_info "Validating environment and prerequisites..."
    
    # Validate environment
    if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
        log_error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
        exit 1
    fi
    
    # Validate cloud
    if [[ ! "$CLOUD" =~ ^(aws|azure|gcp)$ ]]; then
        log_error "Invalid cloud: $CLOUD. Must be 'aws', 'azure', or 'gcp'"
        exit 1
    fi
    
    # Check current working directory
    log_info "Current working directory: $(pwd)"
    
    # Validate project structure
    log_info "Validating project structure..."
    
    # Check for required directories
    REQUIRED_DIRS=(
        "infrastructure"
        "infrastructure/helm"
        "infrastructure/k8s"
        "backend"
        "frontend"
    )
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [[ ! -d "$dir" ]]; then
            log_error "Required directory not found: $dir"
            log_info "Available directories:"
            ls -la . 2>/dev/null || true
            exit 1
        fi
    done
    
    # Check for required files
    REQUIRED_FILES=(
        "infrastructure/k8s/values-common.yaml"
        "backend/Dockerfile"
        "frontend/Dockerfile"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Required file not found: $file"
            exit 1
        fi
    done
    
    # Check for cloud-specific values file (optional)
    CLOUD_VALUES_FILE="infrastructure/k8s/values-${CLOUD}.yaml"
    if [[ ! -f "$CLOUD_VALUES_FILE" ]]; then
        log_warning "Cloud-specific values file not found: $CLOUD_VALUES_FILE"
        log_warning "Will proceed with common values only"
    fi
    
    # Check required tools
    log_info "Checking required tools..."
    command -v kubectl >/dev/null 2>&1 || { log_error "kubectl is required but not installed."; exit 1; }
    command -v helm >/dev/null 2>&1 || { log_error "Helm is required but not installed."; exit 1; }
    
    # Check cloud-specific tools and environment variables
    case $CLOUD in
        "aws")
            command -v aws >/dev/null 2>&1 || { log_error "AWS CLI is required but not installed."; exit 1; }
            [[ -z "$AWS_ACCOUNT_ID" ]] && log_warning "AWS_ACCOUNT_ID environment variable not set"
            ;;
        "azure")
            command -v az >/dev/null 2>&1 || { log_error "Azure CLI is required but not installed."; exit 1; }
            ;;
        "gcp")
            command -v gcloud >/dev/null 2>&1 || { log_error "Google Cloud CLI is required but not installed."; exit 1; }
            [[ -z "$GCP_PROJECT_ID" ]] && log_warning "GCP_PROJECT_ID environment variable not set"
            ;;
    esac
    
    # Check file permissions
    log_info "Checking file permissions..."
    if [[ ! -r "infrastructure/k8s/values-common.yaml" ]]; then
        log_error "Cannot read values-common.yaml - permission denied"
        exit 1
    fi
    
    if [[ ! -r "backend/Dockerfile" ]]; then
        log_error "Cannot read backend/Dockerfile - permission denied"
        exit 1
    fi
    
    if [[ ! -r "frontend/Dockerfile" ]]; then
        log_error "Cannot read frontend/Dockerfile - permission denied"
        exit 1
    fi
    
    log_success "Environment validation completed"
}

# Configure kubectl for the target cloud
configure_kubectl() {
    log_info "Configuring kubectl for $CLOUD $ENVIRONMENT..."
    
    case $CLOUD in
        "aws")
            aws eks update-kubeconfig \
                --region us-west-2 \
                --name "${PROJECT_NAME}-eks-${ENVIRONMENT}" \
                --alias "${CLOUD}-${ENVIRONMENT}"
            ;;
        "azure")
            az aks get-credentials \
                --resource-group "${PROJECT_NAME}-${ENVIRONMENT}" \
                --name "${PROJECT_NAME}-aks-${ENVIRONMENT}" \
                --overwrite-existing
            ;;
        "gcp")
            gcloud container clusters get-credentials \
                "${PROJECT_NAME}-gke-${ENVIRONMENT}" \
                --region us-central1 \
                --project "${GCP_PROJECT_ID}"
            ;;
    esac
    
    # Verify connection
    if kubectl cluster-info >/dev/null 2>&1; then
        log_success "Successfully connected to $CLOUD $ENVIRONMENT cluster"
    else
        log_error "Failed to connect to $CLOUD $ENVIRONMENT cluster"
        exit 1
    fi
}

# Create namespace if it doesn't exist
ensure_namespace() {
    log_info "Ensuring namespace $NAMESPACE exists..."
    
    if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
        log_info "Namespace $NAMESPACE already exists"
    else
        kubectl create namespace "$NAMESPACE"
        log_success "Created namespace $NAMESPACE"
    fi
}

# Manage Kubernetes secrets
manage_secrets() {
    log_info "Managing Kubernetes secrets..."
    
    # Check if secrets exist
    if kubectl get secret "${PROJECT_NAME}-secrets" -n "$NAMESPACE" >/dev/null 2>&1; then
        log_info "Secrets already exist, skipping creation"
    else
        log_warning "Secrets do not exist. This is expected for first deployment."
        log_warning "Please ensure secrets are created manually or via your CI/CD system"
    fi
}

# Run database migrations if needed
run_migrations() {
    log_info "Running database migrations..."
    
    # Create a temporary job for migrations
    kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: ${PROJECT_NAME}-migrate-${VERSION}
  namespace: ${NAMESPACE}
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: ${PROJECT_NAME}/backend:${VERSION}
        command: ["python", "-m", "alembic", "upgrade", "head"]
        envFrom:
        - secretRef:
            name: ${PROJECT_NAME}-secrets
      restartPolicy: Never
  backoffLimit: 3
EOF
    
    # Wait for migration to complete
    kubectl wait --for=condition=complete job/${PROJECT_NAME}-migrate-${VERSION} -n "$NAMESPACE" --timeout=300s
    
    # Clean up migration job
    kubectl delete job ${PROJECT_NAME}-migrate-${VERSION} -n "$NAMESPACE" || true
    
    log_success "Database migrations completed"
}

# Deploy using Helm
deploy_application() {
    log_info "Deploying application using Helm..."
    
    # Validate required files exist
    HELM_CHART_PATH="./infrastructure/helm/xfinity-ai"
    COMMON_VALUES_PATH="./infrastructure/k8s/values-common.yaml"
    CLOUD_VALUES_PATH="./infrastructure/k8s/values-${CLOUD}.yaml"
    
    if [[ ! -d "$HELM_CHART_PATH" ]]; then
        log_error "Helm chart not found at: $HELM_CHART_PATH"
        log_info "Current directory: $(pwd)"
        log_info "Available files:"
        ls -la infrastructure/ 2>/dev/null || log_error "infrastructure/ directory not found"
        exit 1
    fi
    
    if [[ ! -f "$COMMON_VALUES_PATH" ]]; then
        log_error "Common values file not found at: $COMMON_VALUES_PATH"
        log_info "Available k8s files:"
        ls -la infrastructure/k8s/ 2>/dev/null || log_error "k8s/ directory not found"
        exit 1
    fi
    
    if [[ ! -f "$CLOUD_VALUES_PATH" ]]; then
        log_warning "Cloud-specific values file not found at: $CLOUD_VALUES_PATH"
        log_info "Proceeding with common values only"
        CLOUD_VALUES_ARG=""
    else
        CLOUD_VALUES_ARG="--values=$CLOUD_VALUES_PATH"
    fi
    
    # Determine image registry based on cloud
    case $CLOUD in
        "aws")
            IMAGE_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com"
            ;;
        "azure")
            IMAGE_REGISTRY="${PROJECT_NAME}acr${ENVIRONMENT}.azurecr.io"
            ;;
        "gcp")
            IMAGE_REGISTRY="us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/${PROJECT_NAME}-${ENVIRONMENT}"
            ;;
    esac
    
    # Build Helm command with proper error handling
    HELM_CMD="helm upgrade --install ${PROJECT_NAME}-${CLOUD} \
        $HELM_CHART_PATH \
        --namespace=$NAMESPACE \
        --create-namespace \
        --values=$COMMON_VALUES_PATH"
    
    # Add cloud-specific values if available
    if [[ -n "$CLOUD_VALUES_ARG" ]]; then
        HELM_CMD="$HELM_CMD $CLOUD_VALUES_ARG"
    fi
    
    # Add dynamic values
    HELM_CMD="$HELM_CMD \
        --set global.environment=$ENVIRONMENT \
        --set global.cloud=$CLOUD \
        --set global.image.backend.repository=${IMAGE_REGISTRY}/${PROJECT_NAME}/backend \
        --set global.image.backend.tag=$VERSION \
        --set global.image.frontend.repository=${IMAGE_REGISTRY}/${PROJECT_NAME}/frontend \
        --set global.image.frontend.tag=$VERSION \
        --wait \
        --timeout=10m"
    
    log_info "Executing Helm deployment..."
    log_info "Command: $HELM_CMD"
    
    # Execute Helm command with error handling
    if eval "$HELM_CMD"; then
        log_success "Application deployed successfully"
    else
        log_error "Helm deployment failed"
        log_info "Checking Helm release status..."
        helm status "${PROJECT_NAME}-${CLOUD}" -n "$NAMESPACE" || true
        log_info "Checking pod status..."
        kubectl get pods -n "$NAMESPACE" || true
        exit 1
    fi
}

# Run health checks
run_health_checks() {
    log_info "Running health checks..."
    
    # Wait for deployments to be ready
    kubectl rollout status deployment/${PROJECT_NAME}-backend -n "$NAMESPACE" --timeout=300s
    kubectl rollout status deployment/${PROJECT_NAME}-frontend -n "$NAMESPACE" --timeout=300s
    
    # Check pod status
    kubectl get pods -n "$NAMESPACE" -l cloud="$CLOUD"
    
    # Run basic connectivity test
    BACKEND_POD=$(kubectl get pods -n "$NAMESPACE" -l app=backend,cloud="$CLOUD" -o jsonpath='{.items[0].metadata.name}')
    if kubectl exec -n "$NAMESPACE" "$BACKEND_POD" -- curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_success "Backend health check passed"
    else
        log_warning "Backend health check failed or not accessible"
    fi
    
    log_success "Health checks completed"
}

# Generate deployment report
generate_report() {
    log_info "Generating deployment report..."
    
    cat > deployment-report.txt <<EOF
==================================================
DEPLOYMENT REPORT
==================================================
Project: $PROJECT_NAME
Environment: $ENVIRONMENT
Cloud: $CLOUD
Version: $VERSION
Namespace: $NAMESPACE
Deployment Time: $(date)

Deployed Resources:
$(kubectl get all -n "$NAMESPACE" -l cloud="$CLOUD")

Ingress Information:
$(kubectl get ingress -n "$NAMESPACE" 2>/dev/null || echo "No ingress found")

Recent Events:
$(kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -10)
==================================================
EOF
    
    log_success "Deployment report generated: deployment-report.txt"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary resources..."
    # Add any cleanup logic here
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    log_info "Starting CI/CD deployment process..."
    log_info "Project: $PROJECT_NAME"
    log_info "Environment: $ENVIRONMENT"
    log_info "Cloud: $CLOUD"
    log_info "Version: $VERSION"
    log_info "Namespace: $NAMESPACE"
    
    validate_environment
    configure_kubectl
    ensure_namespace
    manage_secrets
    
    # Run migrations only for production
    if [[ "$ENVIRONMENT" == "production" ]]; then
        run_migrations
    fi
    
    deploy_application
    run_health_checks
    generate_report
    cleanup
    
    log_success "🎉 Deployment completed successfully!"
    log_info "Application is available at: https://${ENVIRONMENT}.xfinity-ai.com"
}

# Error handling
trap 'log_error "Deployment failed at line $LINENO. Exit code: $?"' ERR

# Run main function
main "$@" 