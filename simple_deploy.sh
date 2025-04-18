#!/bin/bash
set -e

echo "----------------------------------------------------"
echo "Deploying simplified GBP scraper test app"
echo "----------------------------------------------------"

# Set project ID
PROJECT_ID="clean-code-app-1744825963"

# Make sure gcloud is using the correct project
echo "Setting project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Copy essential files to a temporary directory
DEPLOY_TMP="/tmp/simple_deploy"
rm -rf ${DEPLOY_TMP} || true
mkdir -p ${DEPLOY_TMP}

# Copy only the essential files
cp app.yaml ${DEPLOY_TMP}/
cp simple_app.py ${DEPLOY_TMP}/main.py
cp requirements.txt ${DEPLOY_TMP}/

# Create simplified app.yaml file
cat > ${DEPLOY_TMP}/app.yaml << 'EOF'
runtime: python311
service: default
instance_class: F1

env_variables:
  PROJECT_ID: "clean-code-app-1744825963"
  USE_SECRET_MANAGER: "true"
  GOOGLE_CLOUD_PROJECT: "clean-code-app-1744825963"

automatic_scaling:
  max_instances: 2
  
handlers:
- url: /.*
  script: auto
  secure: always
EOF

# Deploy the application
echo "Deploying application to App Engine..."
cd ${DEPLOY_TMP}
gcloud app deploy app.yaml --quiet

echo "Deployment complete! Check logs for any issues:"
echo "gcloud app logs tail -s default"

echo "Open the application in your browser:"
echo "gcloud app browse"