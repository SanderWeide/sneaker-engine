# Deployment Instructions

## Prerequisites

1.  **Domain Setup**:
    *   Go to the AWS Console -> Route53.
    *   Create a Hosted Zone for `sneaker-engine.com`.
    *   Note the Nameservers (NS records) created.
    *   Go to Squarespace and update the Nameservers for your domain to point to the AWS Nameservers.

2.  **Terraform Setup**:
    *   Ensure you have Terraform installed.
    *   Ensure you have AWS credentials configured.

## Environments

We have two environments:
*   **Development (`dev`)**: `dev.sneaker-engine.com` (Frontend), `api-dev.sneaker-engine.com` (Backend)
*   **Production (`prd`)**: `www.sneaker-engine.com` (Frontend), `api.sneaker-engine.com` (Backend)

## Provisioning Infrastructure

Use the `provision.sh` script to create or update infrastructure for a specific environment. This script handles Terraform workspaces and variable files.

```bash
# Provision Development
./provision.sh dev

# Provision Production
./provision.sh prd
```

## Deploying Application Code

After provisioning the infrastructure, use the `deploy-all.sh` script to build and deploy the application code.

The `deploy-all.sh` script automatically detects the current environment from the Terraform workspace.

```bash
# Deploy to Development
terraform workspace select dev
./deploy-all.sh

# Deploy to Production
terraform workspace select prd
./deploy-all.sh
```

## Cost Management (Development)

To save costs, you can destroy the development environment when not in use.

```bash
# Destroy Development Environment
./destroy.sh dev
```

**Note**: This will delete the database! Only do this if you don't need to persist data.

## Secrets

The `dev.tfvars` and `prd.tfvars` files contain sensitive information (database passwords, JWT secrets). **Do not commit these files to version control** if this is a public repository. Consider using AWS Secrets Manager or environment variables for sensitive data in a real production setup.
