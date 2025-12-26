#!/bin/bash
set -e

ENV=$1

if [ -z "$ENV" ]; then
  echo "Usage: ./provision.sh <dev|prd>"
  exit 1
fi

if [ "$ENV" != "dev" ] && [ "$ENV" != "prd" ]; then
  echo "Error: Environment must be 'dev' or 'prd'"
  exit 1
fi

echo "Switching to workspace: $ENV"
terraform workspace select $ENV || terraform workspace new $ENV

echo "Applying Terraform configuration for $ENV..."
terraform apply -var-file="$ENV.tfvars"
