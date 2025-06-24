#!/bin/bash

# ================================
# CONTEXT ACCESS VALIDATION SCRIPT
# ================================

set -e

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

# Test Docker context access
test_docker_context() {
    log_info "Testing Docker build context access..."
    
    # Test backend context
    if [[ -f "backend/Dockerfile" ]]; then
        log_success "✅ Backend Dockerfile found"
        
        # Test if we can read the Dockerfile
        if [[ -r "backend/Dockerfile" ]]; then
            log_success "✅ Backend Dockerfile is readable"
            log_info "Backend Dockerfile preview:"
            head -5 backend/Dockerfile | sed 's/^/    /'
        else
            log_error "❌ Backend Dockerfile is not readable"
            return 1
        fi
        
        # Test if requirements.txt exists (needed by Dockerfile)
        if [[ -f "backend/requirements.txt" ]]; then
            log_success "✅ Backend requirements.txt found"
        else
            log_error "❌ Backend requirements.txt not found (required by Dockerfile)"
            return 1
        fi
        
        # Test if src directory exists
        if [[ -d "backend/src" ]]; then
            log_success "✅ Backend src directory found"
        else
            log_error "❌ Backend src directory not found (required by Dockerfile)"
            return 1
        fi
    else
        log_error "❌ Backend Dockerfile not found"
        return 1
    fi
    
    # Test frontend context
    if [[ -f "frontend/Dockerfile" ]]; then
        log_success "✅ Frontend Dockerfile found"
        
        # Test if we can read the Dockerfile
        if [[ -r "frontend/Dockerfile" ]]; then
            log_success "✅ Frontend Dockerfile is readable"
            log_info "Frontend Dockerfile preview:"
            head -5 frontend/Dockerfile | sed 's/^/    /'
        else
            log_error "❌ Frontend Dockerfile is not readable"
            return 1
        fi
        
        # Test if package.json exists (needed by Dockerfile)
        if [[ -f "frontend/package.json" ]]; then
            log_success "✅ Frontend package.json found"
        else
            log_error "❌ Frontend package.json not found (required by Dockerfile)"
            return 1
        fi
        
        # Test if nginx.conf exists (needed by Dockerfile)
        if [[ -f "frontend/nginx.conf" ]]; then
            log_success "✅ Frontend nginx.conf found"
        else
            log_error "❌ Frontend nginx.conf not found (required by Dockerfile)"
            return 1
        fi
    else
        log_error "❌ Frontend Dockerfile not found"
        return 1
    fi
    
    log_success "Docker context access test completed"
}

# Test Kubernetes/Helm context access
test_k8s_context() {
    log_info "Testing Kubernetes/Helm context access..."
    
    # Test infrastructure directory structure
    REQUIRED_DIRS=(
        "infrastructure"
        "infrastructure/helm"
        "infrastructure/k8s"
    )
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [[ -d "$dir" ]]; then
            log_success "✅ Directory found: $dir"
        else
            log_error "❌ Directory not found: $dir"
            return 1
        fi
    done
    
    # Test required files
    REQUIRED_FILES=(
        "infrastructure/k8s/values-common.yaml"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "✅ File found: $file"
            if [[ -r "$file" ]]; then
                log_success "✅ File is readable: $file"
            else
                log_error "❌ File is not readable: $file"
                return 1
            fi
        else
            log_error "❌ File not found: $file"
            return 1
        fi
    done
    
    # Test cloud-specific values files
    CLOUD_FILES=(
        "infrastructure/k8s/values-aws.yaml"
        "infrastructure/k8s/values-azure.yaml"
        "infrastructure/k8s/values-gcp.yaml"
    )
    
    for file in "${CLOUD_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "✅ Cloud-specific file found: $file"
        else
            log_warning "⚠️ Cloud-specific file not found: $file (optional)"
        fi
    done
    
    # Test Helm chart structure
    if [[ -d "infrastructure/helm/xfinity-ai" ]]; then
        log_success "✅ Helm chart directory found"
        
        # Check for Chart.yaml
        if [[ -f "infrastructure/helm/xfinity-ai/Chart.yaml" ]]; then
            log_success "✅ Chart.yaml found"
        else
            log_error "❌ Chart.yaml not found in Helm chart"
            return 1
        fi
        
        # Check for templates directory
        if [[ -d "infrastructure/helm/xfinity-ai/templates" ]]; then
            log_success "✅ Helm templates directory found"
        else
            log_error "❌ Helm templates directory not found"
            return 1
        fi
    else
        log_error "❌ Helm chart directory not found: infrastructure/helm/xfinity-ai"
        return 1
    fi
    
    log_success "Kubernetes/Helm context access test completed"
}

# Test file permissions
test_permissions() {
    log_info "Testing file permissions..."
    
    # Test script permissions
    if [[ -x "infrastructure/scripts/ci-cd-deploy.sh" ]]; then
        log_success "✅ Deployment script is executable"
    else
        log_warning "⚠️ Deployment script is not executable (may need chmod +x)"
    fi
    
    # Test write permissions in current directory
    if touch test-write-permission 2>/dev/null; then
        rm -f test-write-permission
        log_success "✅ Write permissions available in current directory"
    else
        log_error "❌ No write permissions in current directory"
        return 1
    fi
    
    log_success "File permissions test completed"
}

# Test environment variables
test_environment_vars() {
    log_info "Testing environment variables..."
    
    # Check for common environment variables
    ENV_VARS=(
        "AWS_ACCOUNT_ID"
        "GCP_PROJECT_ID"
        "AZURE_SUBSCRIPTION_ID"
    )
    
    for var in "${ENV_VARS[@]}"; do
        if [[ -n "${!var}" ]]; then
            log_success "✅ Environment variable set: $var"
        else
            log_warning "⚠️ Environment variable not set: $var (may be needed for $var deployment)"
        fi
    done
    
    log_success "Environment variables test completed"
}

# Main test function
main() {
    log_info "🧪 Starting context access validation tests..."
    log_info "Current directory: $(pwd)"
    
    # Run all tests
    test_docker_context
    test_k8s_context
    test_permissions
    test_environment_vars
    
    log_success "🎉 All context access tests completed successfully!"
    log_info "Your environment is ready for CI/CD deployment."
}

# Error handling
trap 'log_error "Context access test failed at line $LINENO"' ERR

# Run main function
main "$@" 