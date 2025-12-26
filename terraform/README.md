# Sneaker Engine - AWS Deployment with Terraform

This directory contains Terraform configuration files to deploy the Sneaker Engine application to AWS using:
- **ECS Fargate** for the backend API
- **RDS PostgreSQL** for the database
- **S3 + CloudFront** for the frontend

## Architecture Overview

```
┌─────────────────┐
│   CloudFront    │ ──► Frontend (Angular)
└─────────────────┘
         │
         │ HTTPS
         │
         ▼
┌─────────────────┐
│   S3 Bucket     │ (Static Website Hosting)
└─────────────────┘

┌─────────────────┐
│   Users/Apps    │
└─────────────────┘
         │
         │ HTTP/HTTPS
         ▼
┌─────────────────┐
│  Load Balancer  │ (Application Load Balancer)
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   ECS Fargate   │ ──► Backend API (FastAPI)
│  (Auto Scaling) │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ RDS PostgreSQL  │ (Database)
└─────────────────┘
```

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
  [AWS CLI install page](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
3. **Terraform** installed (>= 1.0)
  [Terraform install page](https://developer.hashicorp.com/terraform/install#linux)
4. **Docker** installed for building backend image

## Configuration

### 1. Create a `terraform.tfvars` file

Create a file named `terraform.tfvars` in this directory with your configuration:

```hcl
# Required Variables
aws_region  = "eu-central-1"  # Default region
environment = "dev"

# Database Configuration
db_password = "your-secure-database-password"  # Change this!
db_username = "postgres"
db_name     = "sneaker_engine"

# JWT Configuration
jwt_secret_key         = "your-super-secret-jwt-key"  # Change this!
jwt_algorithm          = "HS256"
jwt_expiration_minutes = 1440

# Optional: Adjust resources
backend_cpu            = 256
backend_memory         = 512
backend_desired_count  = 1

# Optional: Custom domain (requires ACM certificate)
# frontend_domain_name = "app.yourdomain.com"
# acm_certificate_arn  = "arn:aws:acm:eu-central-1:123456789:certificate/xxx"
```

**IMPORTANT:** Never commit `terraform.tfvars` to git! It's already in `.gitignore`.

### 2. Environment Variables (Alternative)

You can also set sensitive values via environment variables:

```bash
export TF_VAR_db_password="your-secure-password"
export TF_VAR_jwt_secret_key="your-super-secret-key"
export TF_VAR_aws_region="eu-central-1"  # Or your preferred region
```

## Deployment Steps

### Step 1: Initialize Terraform

```bash
cd terraform
terraform init
```

This downloads required providers and initializes the backend.

**Note:** There are deployment scripts (`deploy-backend.sh`, `deploy-frontend.sh`, `deploy-all.sh`) available to automate many of the following steps. These only work for updating when there is already infra running

### Step 2: Review the Plan

```bash
terraform plan
```

Review the resources that will be created. Should show ~50+ resources.

### Step 3: Apply the Configuration

```bash
terraform apply
```

Type `yes` when prompted. This will take 10-15 minutes to create all resources.

### Step 4: Build and Push Backend Docker Image

After Terraform completes, get the ECR repository URL:

```bash
ECR_URL=$(terraform output -raw ecr_repository_url)
AWS_REGION="eu-central-1"  # Or get from: terraform output -raw aws_region (if exposed)
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
```

Authenticate Docker to ECR:

```bash
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URL
```

Build and push the backend image:

```bash
cd ../backend
docker build -t sneaker-engine-backend:latest .
docker tag sneaker-engine-backend:latest $ECR_URL:latest
docker push $ECR_URL:latest
```

### Step 5: Run Database Migrations

Get the RDS endpoint and connect to run migrations:

```bash
cd ../terraform
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
DB_NAME=$(terraform output -raw rds_database_name)

# Connect via ECS Exec or use a bastion host
# For production, use AWS Systems Manager Session Manager or a bastion host
```

**Note:** Migrations should run automatically when the ECS task starts (if configured in the backend startup). Otherwise, you'll need to set up a way to run migrations. Options include:
1. ECS Exec into a running task
2. A bastion EC2 instance in the VPC
3. A one-time ECS task for migrations

### Step 6: Deploy Frontend to S3

Build the Angular frontend:

```bash
cd ../frontend
npm install
npm run build
```

Get the S3 bucket name and sync files:

```bash
cd ../terraform
S3_BUCKET=$(terraform output -raw frontend_bucket_name)
CLOUDFRONT_ID=$(terraform output -raw cloudfront_distribution_id)

aws s3 sync ../frontend/dist/frontend/browser/ s3://$S3_BUCKET/ --delete
```

Invalidate CloudFront cache:

```bash
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"
```

### Step 7: Update ECS Service

Force a new deployment to use the Docker image:

```bash
CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
aws ecs update-service --cluster $CLUSTER_NAME --service sneaker-engine-dev-backend-service --force-new-deployment
```

### Step 8: Get Application URLs

```bash
echo "Backend API: $(terraform output -raw backend_url)"
echo "Frontend URL: $(terraform output -raw frontend_url)"
```

## Configuration Management

### Update Environment Variables

To update environment variables in ECS:

1. Update the `environment` or `secrets` blocks in `ecs.tf`
2. Run `terraform apply`
3. Force a new deployment: `aws ecs update-service --cluster <cluster> --service <service> --force-new-deployment`

### Update Backend Code

```bash
# Build and push new image
cd backend
docker build -t sneaker-engine-backend:latest .
docker tag sneaker-engine-backend:latest $ECR_URL:latest
docker push $ECR_URL:latest

# Force ECS to deploy new version
aws ecs update-service --cluster <cluster-name> --service <service-name> --force-new-deployment

# Or use the deployment script:
cd ../terraform
./deploy-backend.sh
```

### Update Frontend

```bash
# Build and deploy
cd frontend
npm run build
aws s3 sync dist/frontend/browser/ s3://$S3_BUCKET/ --delete
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"

# Or use the deployment script:
cd ../terraform
./deploy-frontend.sh
```

## Monitoring & Logs

### View Backend Logs

```bash
# Using AWS CLI
aws logs tail /ecs/sneaker-engine-dev/backend --follow

# Or in AWS Console
# CloudWatch > Log groups > /ecs/sneaker-engine-dev/backend
```

### View ECS Service Status

```bash
aws ecs describe-services --cluster <cluster-name> --services <service-name>
```

### Monitor Auto Scaling

```bash
aws application-autoscaling describe-scaling-activities \
  --service-namespace ecs \
  --resource-id service/<cluster-name>/<service-name>
```

## Cost Optimization

### Development Environment

For development, you can reduce costs:

```hcl
# In terraform.tfvars
availability_zones_count = 1  # Use only 1 AZ (reduces NAT Gateway costs)
backend_cpu             = 256
backend_memory          = 512
db_instance_class       = "db.t3.micro"
```

### Production Considerations

For production:
- Increase `availability_zones_count` to 2 or 3
- Use larger instance types
- Enable RDS deletion protection
- Use Multi-AZ for RDS
- Consider using FARGATE_SPOT for cost savings

## Security Best Practices

1. **Never commit secrets** - Use AWS Secrets Manager or SSM Parameter Store
2. **Enable AWS CloudTrail** for audit logging
3. **Use HTTPS** - Set up ACM certificate and custom domain
4. **Rotate credentials** regularly
5. **Enable VPC Flow Logs** for network monitoring
6. **Use AWS WAF** with CloudFront for DDoS protection
7. **Enable GuardDuty** for threat detection

## Troubleshooting

### ECS Tasks Not Starting

```bash
# Check task status
aws ecs describe-tasks --cluster <cluster> --tasks <task-id>

# Common issues:
# - Image not found: Check ECR repository and image tag
# - Health check failing: Check /api/health endpoint
# - Database connection: Verify security groups and RDS endpoint
```

### Database Connection Issues

1. Check security groups allow traffic on port 5432
2. Verify DATABASE_URL in SSM Parameter Store
3. Check RDS endpoint is correct
4. Ensure ECS tasks are in private subnets with NAT Gateway access

### CloudFront Not Serving Updated Content

```bash
# Invalidate cache
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"
```

## Cleanup

To destroy all resources:

```bash
# CAUTION: This will delete everything!
terraform destroy
```

Type `yes` to confirm. This will take several minutes.

**Note:** If deletion fails due to non-empty S3 bucket:

```bash
aws s3 rm s3://$S3_BUCKET --recursive
terraform destroy
```

## Resource Naming Convention

All resources follow this pattern:
```
{project_name}-{environment}-{resource_type}
```

Example:
- VPC: `sneaker-engine-dev-vpc`
- ECS Cluster: `sneaker-engine-dev-cluster`
- RDS Instance: `sneaker-engine-dev-db`

## Terraform State Management

Currently using local state. For production, use remote state:

```hcl
# In main.tf, uncomment:
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "sneaker-engine/terraform.tfstate"
    region         = "eu-central-1"  # Match your AWS region
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

Create the S3 bucket and DynamoDB table first:

```bash
aws s3 mb s3://your-terraform-state-bucket --region eu-central-1
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region eu-central-1
```

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-central-1  # Or use: ${{ vars.AWS_REGION }}
      
      - name: Login to ECR
        run: aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URL
      
      - name: Build and push
        run: |
          docker build -t sneaker-engine-backend:latest ./backend
          docker tag sneaker-engine-backend:latest $ECR_URL:latest
          docker push $ECR_URL:latest
      
      - name: Deploy to ECS
        run: aws ecs update-service --cluster <cluster> --service <service> --force-new-deployment

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Build frontend
        run: |
          cd frontend
          npm ci
          npm run build
      
      - name: Deploy to S3
        run: aws s3 sync frontend/dist/sneaker-engine/ s3://$S3_BUCKET/ --delete
      
      - name: Invalidate CloudFront
        run: aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"
```

## Additional Resources

- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/intro.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Angular Deployment](https://angular.io/guide/deployment)

## Support

For issues or questions:
1. Check CloudWatch logs for backend errors
2. Check browser console for frontend errors
3. Review Terraform plan output for configuration issues
4. Check AWS service limits and quotas
