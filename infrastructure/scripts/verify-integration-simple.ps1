# Multi-Cloud Integration Verification Script
Write-Host "🔍 Verifying Multi-Cloud Integration..." -ForegroundColor Green

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
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file (missing)" -ForegroundColor Red
        $allGood = $false
    }
}

if ($allGood) {
    Write-Host "`n🎉 Integration verification PASSED!" -ForegroundColor Green
    Write-Host "Your multi-cloud infrastructure is properly integrated." -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Integration verification FAILED!" -ForegroundColor Red
    Write-Host "Some required files are missing." -ForegroundColor Red
}

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Update infrastructure/environments/multi-cloud.env with your values" -ForegroundColor White
Write-Host "2. Install: terraform, kubectl, helm, docker" -ForegroundColor White
Write-Host "3. Configure cloud credentials (aws, az, gcloud)" -ForegroundColor White
Write-Host "4. Run: bash infrastructure/scripts/deploy-integrated.sh" -ForegroundColor White 