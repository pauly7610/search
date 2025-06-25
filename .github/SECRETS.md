# Repository Secrets Configuration

This document describes the required secrets for the CI/CD workflows to function properly.

## Required Secrets

### Core Application Secrets

- `SECRET_KEY` - Application secret key for cryptographic operations
- `DATABASE_URL` - Production database connection string
- `REDIS_URL` - Redis connection string for caching

### AWS Configuration (for AWS deployments)

- `AWS_ACCESS_KEY_ID` - AWS access key ID
- `AWS_SECRET_ACCESS_KEY` - AWS secret access key
- `AWS_ACCOUNT_ID` - AWS account ID for ECR registry
- `AWS_REGION` - AWS region (default: us-west-2)

### Azure Configuration (for Azure deployments)

- `AZURE_REGISTRY_LOGIN_SERVER` - Azure Container Registry login server
- `AZURE_REGISTRY_USERNAME` - Azure Container Registry username
- `AZURE_REGISTRY_PASSWORD` - Azure Container Registry password

### Google Cloud Configuration (for GCP deployments)

- `GCP_SA_KEY` - Google Cloud Service Account JSON key
- `GCP_PROJECT_ID` - Google Cloud Project ID

### Notification Configuration (optional)

- `SLACK_WEBHOOK_URL` - Slack webhook URL for deployment notifications

## Setting up Secrets

1. Go to your repository Settings
2. Click on "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add each secret with its corresponding value

## Security Notes

- **Never commit secrets to your repository**
- Use separate secrets for staging and production environments
- Rotate secrets regularly
- Use least-privilege access for service accounts
- Monitor secret usage in workflow runs

## Workflow Behavior

- Workflows will continue execution even if optional secrets are missing
- Missing required secrets will cause deployment steps to fail gracefully
- All cloud provider steps have `continue-on-error: true` to prevent workflow failures

## Testing Locally

For local development, create a `.env` file with these variables:

```bash
SECRET_KEY=your-local-secret-key
DATABASE_URL=postgresql://localhost:5432/xfinity_ai_dev
REDIS_URL=redis://localhost:6379/0
```

**Note**: Never commit the `.env` file to version control.

## Troubleshooting

### Common Issues

1. **"Context access might be invalid" errors**

   - These warnings appear when secrets are referenced but not configured
   - Add the required secrets to resolve these warnings

2. **Deployment failures**

   - Check that cloud provider credentials are correctly configured
   - Verify that the service accounts have necessary permissions

3. **Notification failures**
   - Ensure `SLACK_WEBHOOK_URL` is properly formatted
   - Test the webhook URL manually before adding to secrets

### Verification

To verify your secrets are working:

1. Check the Actions tab after pushing changes
2. Look for successful authentication steps in workflow logs
3. Verify that deployment notifications are received (if Slack is configured)

## Support

If you encounter issues with secret configuration:

1. Check the workflow logs for specific error messages
2. Verify secret names match exactly (they are case-sensitive)
3. Ensure all required permissions are granted to service accounts
