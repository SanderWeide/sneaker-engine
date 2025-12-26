#!/bin/bash
set -e

cd "$(dirname "$0")"

# Get outputs from Terraform
S3_BUCKET=$(terraform output -raw frontend_bucket_name)
CLOUDFRONT_ID=$(terraform output -raw cloudfront_distribution_id)

echo "Building and deploying frontend..."

# Build Angular app
cd ../frontend
npm run build

# Deploy to S3 (sync only browser directory contents to root)
aws s3 sync dist/frontend/browser/ s3://$S3_BUCKET/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"

echo "Frontend deployed!"
