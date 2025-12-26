#!/bin/bash
set -e

ENV=$1

if [ -z "$ENV" ]; then
  echo "Usage: ./destroy.sh <dev|prd>"
  exit 1
fi

if [ "$ENV" != "dev" ] && [ "$ENV" != "prd" ]; then
  echo "Error: Environment must be 'dev' or 'prd'"
  exit 1
fi

echo "WARNING: You are about to DESTROY the $ENV environment."
echo "This will delete all resources (Load Balancers, Databases, etc.) for $ENV."
read -p "Are you sure? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo "Switching to workspace: $ENV"
terraform workspace select $ENV

echo "Destroying Terraform configuration for $ENV..."
terraform destroy -var-file="$ENV.tfvars"
