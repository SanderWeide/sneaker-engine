#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Deploying backend..."
./deploy-backend.sh

echo ""
echo "Deploying frontend..."
./deploy-frontend.sh

echo ""
echo "Deployment complete!"
echo "Backend:  $(terraform output -raw backend_url)"
echo "Frontend: $(terraform output -raw frontend_url)"
