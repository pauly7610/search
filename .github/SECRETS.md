# GitHub Secrets Configuration Guide

This document describes the secrets you need to configure in your GitHub repository for the multi-cloud CI/CD pipeline to work properly.

## Required GitHub Secrets

### Core Application Secrets

| Secret Name      | Description                                 | Example Value                       |
| ---------------- | ------------------------------------------- | ----------------------------------- |
| `SECRET_KEY`     | 32-character secret key for the application | `your-32-character-secret-key-here` |
| `OPENAI_API_KEY` | OpenAI API key for AI features              | `sk-proj-...`                       |

### AWS Secrets

| Secret Name             | Description                 | Example Value                                                                         |
| ----------------------- | --------------------------- | ------------------------------------------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | AWS Access Key ID           | `AKIAIOSFODNN7EXAMPLE`                                                                |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key       | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`                                            |
| `AWS_ACCOUNT_ID`        | AWS Account ID              | `123456789012`                                                                        |
| `AWS_CERTIFICATE_ARN`   | SSL Certificate ARN for ALB | `arn:aws:acm:us-west-2:123456789012:certificate/12345678-1234-1234-1234-123456789012` |

### Azure Secrets

| Secret Name                   | Description                       | Example Value                          |
| ----------------------------- | --------------------------------- | -------------------------------------- |
| `AZURE_REGISTRY_LOGIN_SERVER` | Azure Container Registry URL      | `xfinityaiacr.azurecr.io`              |
| `AZURE_REGISTRY_USERNAME`     | Azure Container Registry Username | `xfinityaiacr`                         |
| `AZURE_REGISTRY_PASSWORD`     | Azure Container Registry Password | `generated-password`                   |
| `AZURE_SUBSCRIPTION_ID`       | Azure Subscription ID             | `12345678-1234-1234-1234-123456789012` |
| `AZURE_TENANT_ID`             | Azure Tenant ID                   | `12345678-1234-1234-1234-123456789012` |

### Google Cloud Platform Secrets

| Secret Name      | Description                               | Example Value                                  |
| ---------------- | ----------------------------------------- | ---------------------------------------------- |
| `GCP_SA_KEY`     | Service Account JSON Key (base64 encoded) | `ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsC...` |
| `GCP_PROJECT_ID` | Google Cloud Project ID                   | `xfinity-ai-production`                        |

### Database Secrets

| Secret Name   | Description                            | Example Value                   |
| ------------- | -------------------------------------- | ------------------------------- |
| `DB_PASSWORD` | Database password for all environments | `your-secure-database-password` |

### Notification Secrets (Optional)

| Secret Name         | Description                                | Example Value                          |
| ------------------- | ------------------------------------------ | -------------------------------------- |
| `SLACK_WEBHOOK_URL` | Slack webhook for deployment notifications | `https://hooks.slack.com/services/...` |

## How to Set Up Secrets

### 1. Navigate to Repository Settings

- Go to your repository on GitHub
- Click on "Settings" tab
- Click on "Secrets and variables" in the left sidebar
- Click on "Actions"

### 2. Add Each Secret

- Click "New repository secret"
- Enter the secret name exactly as shown above
- Enter the secret value
- Click "Add secret"

### 3. Verify Secrets

After adding all secrets, verify they appear in your secrets list:

```
AWS_ACCESS_KEY_ID ✓
AWS_SECRET_ACCESS_KEY ✓
AWS_ACCOUNT_ID ✓
AZURE_REGISTRY_LOGIN_SERVER ✓
... (and so on)
```

## Cloud-Specific Setup Instructions

### AWS Setup

1. **Create IAM User**:

   ```bash
   aws iam create-user --user-name github-actions-xfinity-ai
   ```

2. **Attach Required Policies**:

   ```bash
   aws iam attach-user-policy --user-name github-actions-xfinity-ai --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy
   aws iam attach-user-policy --user-name github-actions-xfinity-ai --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess
   ```

3. **Create Access Keys**:
   ```bash
   aws iam create-access-key --user-name github-actions-xfinity-ai
   ```

### Azure Setup

1. **Create Service Principal**:

   ```bash
   az ad sp create-for-rbac --name "github-actions-xfinity-ai" --role contributor --scopes /subscriptions/{subscription-id}
   ```

2. **Get ACR Credentials**:
   ```bash
   az acr credential show --name xfinityaiacr
   ```

### Google Cloud Setup

1. **Create Service Account**:

   ```bash
   gcloud iam service-accounts create github-actions-xfinity-ai --display-name="GitHub Actions Service Account"
   ```

2. **Grant Required Roles**:

   ```bash
   gcloud projects add-iam-policy-binding your-project-id \
     --member="serviceAccount:github-actions-xfinity-ai@your-project-id.iam.gserviceaccount.com" \
     --role="roles/container.developer"
   ```

3. **Create and Download Key**:
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=github-actions-xfinity-ai@your-project-id.iam.gserviceaccount.com
   ```

## Environment-Specific Secrets

You can also create environment-specific secrets by setting up GitHub Environments:

### Staging Environment

- Navigate to Settings → Environments
- Create "staging" environment
- Add environment-specific secrets with `_STAGING` suffix

### Production Environment

- Create "production" environment
- Add environment-specific secrets with `_PRODUCTION` suffix
- Enable required reviewers for production deployments

## Security Best Practices

1. **Rotate Secrets Regularly**: Update all secrets every 90 days
2. **Use Minimal Permissions**: Grant only the permissions necessary for CI/CD
3. **Monitor Secret Usage**: Check GitHub Actions logs for secret access
4. **Enable Audit Logging**: Track who has access to secrets
5. **Use Environment Protection**: Require approvals for production deployments

## Troubleshooting

### Common Issues

1. **Invalid Credentials**: Double-check secret values and permissions
2. **Missing Secrets**: Ensure all required secrets are configured
3. **Wrong Secret Names**: Secret names are case-sensitive
4. **Expired Credentials**: Check if cloud credentials have expired

### Testing Secrets

You can test if secrets are working by running the workflow manually:

- Go to Actions tab
- Select the workflow
- Click "Run workflow"
- Monitor the logs for authentication errors
