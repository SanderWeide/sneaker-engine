#!/bin/bash
set -e

cd "$(dirname "$0")"

# Get outputs from Terraform
S3_BUCKET=$(terraform output -raw frontend_bucket_name)
CLOUDFRONT_ID=$(terraform output -raw cloudfront_distribution_id)
BACKEND_URL=$(terraform output -raw backend_url)
ENV=$(terraform workspace show)

echo "Building and deploying frontend for environment: $ENV"
echo "Using Backend URL: $BACKEND_URL"

# Build Angular app
cd ../frontend

# Determine which environment file to update
ENV_FILE="src/environments/environment.prd.ts"
BUILD_CONFIG="prd"

if [ "$ENV" == "dev" ]; then
  ENV_FILE="src/environments/environment.dev.ts"
  BUILD_CONFIG="dev"
fi

echo "Updating $ENV_FILE..."

# Update environment file with the correct backend URL
# We use a temporary file to avoid issues with sed on different platforms
sed "s|apiUrl: '.*'|apiUrl: '$BACKEND_URL'|" $ENV_FILE > "$ENV_FILE.tmp" && mv "$ENV_FILE.tmp" $ENV_FILE

echo "Running build with configuration: $BUILD_CONFIG"
npm run build -- --configuration=$BUILD_CONFIG

# Revert changes to environment file (optional, but good for local dev)
git checkout $ENV_FILE || true

# Deploy to S3 (sync only browser directory contents to root)
aws s3 sync dist/frontend/browser/ s3://$S3_BUCKET/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"

echo "Frontend deployed!"
