#!/bin/bash
set -e

cd "$(dirname "$0")"

# Get outputs from Terraform
ECR_URL=$(terraform output -raw ecr_repository_url)
REGION=$(terraform output -raw aws_region)
CLUSTER=$(terraform output -raw ecs_cluster_name)

echo "Building and pushing backend..."

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URL

# Build and push
cd ../backend
docker build -t $ECR_URL:latest .
docker push $ECR_URL:latest

# Update ECS service
echo "Updating ECS service..."
SERVICE_NAME=${CLUSTER%-cluster}-backend-service
aws ecs update-service --cluster $CLUSTER --service $SERVICE_NAME --force-new-deployment --region $REGION

echo "Backend deployed!"
