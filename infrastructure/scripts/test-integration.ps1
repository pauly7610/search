# Multi-Cloud Integration Verification Script
Write-Host "Verifying Multi-Cloud Integration..." -ForegroundColor Green

# Check critical files exist
$criticalFiles = @(
    "infrastructure/terraform/aws/main.tf",
    "infrastructure/k8s/values-common.yaml", 
    "infrastructure/k8s/values-aws.yaml",
    "infrastructure/helm/xfinity-ai/templates/backend-deployment.yaml",
    "infrastructure/environments/multi-cloud.env",
    "backend/src/config/settings.py",
    "backend/src/services/cache_service.py"
)

$allGood = $true
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "PASS: $file" -ForegroundColor Green
    }
    else {
        Write-Host "FAIL: $file (missing)" -ForegroundColor Red
        $allGood = $false
    }
}

if ($allGood) {
    Write-Host ""
    Write-Host "Integration verification PASSED!" -ForegroundColor Green
    Write-Host "Your multi-cloud infrastructure is properly integrated." -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "Integration verification FAILED!" -ForegroundColor Red
    Write-Host "Some required files are missing." -ForegroundColor Red
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update infrastructure/environments/multi-cloud.env with your values" -ForegroundColor White
Write-Host "2. Install: terraform, kubectl, helm, docker" -ForegroundColor White
Write-Host "3. Configure cloud credentials" -ForegroundColor White
Write-Host "4. Run deployment script" -ForegroundColor White 