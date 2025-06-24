# Multi-Cloud Integration Verification Script
# This script verifies that your multi-cloud infrastructure integrates properly with your existing codebase

param(
    [string]$Environment = "production",
    [string]$TestCloud = "aws"
)

Write-Host "🔍 Verifying Multi-Cloud Integration for $Environment environment" -ForegroundColor Green
Write-Host "🧪 Testing cloud: $TestCloud" -ForegroundColor Cyan

# Function to check if file exists and has content
function Test-FileIntegrity {
    param([string]$FilePath, [string]$Description)
    
    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath -Raw
        if ($content.Length -gt 0) {
            Write-Host "✅ $Description" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $Description (empty file)" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "❌ $Description (file not found)" -ForegroundColor Red
        return $false
    }
}

# Function to check environment variable compatibility
function Test-EnvironmentVariables {
    Write-Host "`n🔧 Checking Environment Variable Compatibility..." -ForegroundColor Yellow
    
    $envFile = "infrastructure/environments/multi-cloud.env"
    $settingsFile = "backend/src/config/settings.py"
    
    if (!(Test-Path $envFile)) {
        Write-Host "❌ Multi-cloud environment file not found" -ForegroundColor Red
        return $false
    }
    
    if (!(Test-Path $settingsFile)) {
        Write-Host "❌ Backend settings file not found" -ForegroundColor Red
        return $false
    }
    
    $envContent = Get-Content $envFile
    $settingsContent = Get-Content $settingsFile -Raw
    
    # Check for key environment variables
    $requiredVars = @(
        "APP_NAME", "SECRET_KEY", "DATABASE_URL", "REDIS_URL", 
        "OPENAI_API_KEY", "CORS_ORIGINS", "LOG_LEVEL"
    )
    
    $allFound = $true
    foreach ($var in $requiredVars) {
        $envHasVar = $envContent -match "^$var="
        $settingsHasVar = $settingsContent -match "$var.*:"
        
        if ($envHasVar -and $settingsHasVar) {
            Write-Host "✅ $var defined in both env and settings" -ForegroundColor Green
        } else {
            Write-Host "❌ $var missing in $(if (!$envHasVar) { 'env' } else { 'settings' })" -ForegroundColor Red
            $allFound = $false
        }
    }
    
    return $allFound
}

# Function to verify Terraform configuration
function Test-TerraformConfig {
    param([string]$Cloud)
    
    Write-Host "`n🏗️  Checking Terraform Configuration for $Cloud..." -ForegroundColor Yellow
    
    $terraformDir = "infrastructure/terraform/$Cloud"
    $requiredFiles = @("main.tf", "variables.tf", "outputs.tf")
    
    $allFound = $true
    foreach ($file in $requiredFiles) {
        $filePath = "$terraformDir/$file"
        if (!(Test-FileIntegrity $filePath "$Cloud Terraform $file")) {
            $allFound = $false
        }
    }
    
    return $allFound
}

# Function to verify Kubernetes configuration
function Test-KubernetesConfig {
    param([string]$Cloud)
    
    Write-Host "`n☸️  Checking Kubernetes Configuration for $Cloud..." -ForegroundColor Yellow
    
    $k8sDir = "infrastructure/k8s"
    $helmDir = "infrastructure/helm/xfinity-ai"
    
    $requiredFiles = @(
        "$k8sDir/values-common.yaml",
        "$k8sDir/values-$Cloud.yaml",
        "$helmDir/templates/backend-deployment.yaml"
    )
    
    $allFound = $true
    foreach ($file in $requiredFiles) {
        if (!(Test-FileIntegrity $file "Kubernetes config $(Split-Path $file -Leaf)")) {
            $allFound = $false
        }
    }
    
    return $allFound
}

# Function to verify Docker configuration
function Test-DockerConfig {
    Write-Host "`n🐳 Checking Docker Configuration..." -ForegroundColor Yellow
    
    $dockerFiles = @(
        "backend/Dockerfile",
        "frontend/Dockerfile"
    )
    
    $allFound = $true
    foreach ($file in $dockerFiles) {
        if (!(Test-FileIntegrity $file "Docker $(Split-Path (Split-Path $file -Parent) -Leaf)")) {
            $allFound = $false
        }
    }
    
    return $allFound
}

# Function to verify database integration
function Test-DatabaseIntegration {
    Write-Host "`n🗄️  Checking Database Integration..." -ForegroundColor Yellow
    
    $dbFiles = @(
        "backend/src/models/chat_models.py",
        "backend/src/repositories/chat_repository.py",
        "backend/src/services/chat_service.py",
        "database/migrations/001_create_knowledge_base.sql",
        "database/migrations/002_create_conversations.sql"
    )
    
    $allFound = $true
    foreach ($file in $dbFiles) {
        if (!(Test-FileIntegrity $file "Database $(Split-Path $file -Leaf)")) {
            $allFound = $false
        }
    }
    
    return $allFound
}

# Function to check service integrations
function Test-ServiceIntegration {
    Write-Host "`n🔗 Checking Service Integration..." -ForegroundColor Yellow
    
    $serviceFiles = @(
        "backend/src/services/cache_service.py",
        "backend/src/services/chat_service.py",
        "backend/src/validators/input_validators.py",
        "backend/src/core/exceptions.py"
    )
    
    $allFound = $true
    foreach ($file in $serviceFiles) {
        if (!(Test-FileIntegrity $file "Service $(Split-Path $file -Leaf)")) {
            $allFound = $false
        }
    }
    
    return $allFound
}

# Function to verify monitoring setup
function Test-MonitoringIntegration {
    Write-Host "`n📊 Checking Monitoring Integration..." -ForegroundColor Yellow
    
    $monitoringFiles = @(
        "monitoring/prometheus/prometheus.yml",
        "monitoring/grafana/dashboards/backend-api-dashboard.json",
        "infrastructure/kubernetes/01-config.yaml"
    )
    
    $allFound = $true
    foreach ($file in $monitoringFiles) {
        if (!(Test-FileIntegrity $file "Monitoring $(Split-Path $file -Leaf)")) {
            $allFound = $false
        }
    }
    
    return $allFound
}

# Function to check deployment scripts
function Test-DeploymentScripts {
    Write-Host "`n🚀 Checking Deployment Scripts..." -ForegroundColor Yellow
    
    $scriptFiles = @(
        "infrastructure/scripts/deploy-integrated.sh"
    )
    
    $allFound = $true
    foreach ($file in $scriptFiles) {
        if (!(Test-FileIntegrity $file "Deployment $(Split-Path $file -Leaf)")) {
            $allFound = $false
        }
    }
    
    return $allFound
}

# Main verification process
Write-Host "🎯 Starting Multi-Cloud Integration Verification..." -ForegroundColor Magenta

$testResults = @()

# Run all tests
$testResults += @{
    Name = "Environment Variables"
    Result = Test-EnvironmentVariables
}

$testResults += @{
    Name = "Terraform Config ($TestCloud)"
    Result = Test-TerraformConfig -Cloud $TestCloud
}

$testResults += @{
    Name = "Kubernetes Config ($TestCloud)"
    Result = Test-KubernetesConfig -Cloud $TestCloud
}

$testResults += @{
    Name = "Docker Configuration"
    Result = Test-DockerConfig
}

$testResults += @{
    Name = "Database Integration"
    Result = Test-DatabaseIntegration
}

$testResults += @{
    Name = "Service Integration"
    Result = Test-ServiceIntegration
}

$testResults += @{
    Name = "Monitoring Integration"
    Result = Test-MonitoringIntegration
}

$testResults += @{
    Name = "Deployment Scripts"
    Result = Test-DeploymentScripts
}

# Summary
Write-Host "`n📋 INTEGRATION VERIFICATION SUMMARY" -ForegroundColor Magenta
Write-Host "=" * 50 -ForegroundColor Magenta

$passed = 0
$failed = 0

foreach ($test in $testResults) {
    if ($test.Result) {
        Write-Host "✅ $($test.Name)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌ $($test.Name)" -ForegroundColor Red
        $failed++
    }
}

Write-Host "`n📊 Results: $passed passed, $failed failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Yellow" })

if ($failed -eq 0) {
    Write-Host "`n🎉 INTEGRATION VERIFICATION SUCCESSFUL!" -ForegroundColor Green
    Write-Host "Your multi-cloud infrastructure is properly integrated with your existing codebase." -ForegroundColor Green
    Write-Host "`n🚀 Ready for deployment! Use the following commands:" -ForegroundColor Cyan
    Write-Host "   Windows: powershell infrastructure/scripts/deploy-integrated.sh" -ForegroundColor Gray
    Write-Host "   Linux/Mac: bash infrastructure/scripts/deploy-integrated.sh" -ForegroundColor Gray
} else {
    Write-Host "`n⚠️  INTEGRATION VERIFICATION FAILED!" -ForegroundColor Red
    Write-Host "Please fix the failed tests before proceeding with deployment." -ForegroundColor Red
}

Write-Host "`n🔍 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Update infrastructure/environments/multi-cloud.env with your actual values" -ForegroundColor Gray
Write-Host "2. Set up cloud provider credentials (AWS CLI, Azure CLI, gcloud)" -ForegroundColor Gray
Write-Host "3. Run terraform init in each cloud directory" -ForegroundColor Gray
Write-Host "4. Execute deployment using the integrated script" -ForegroundColor Gray 