#!/bin/bash

# deploy.sh - Helper script for deploying to Google App Engine

echo "==== Starting deployment process ===="

# Check if we're in the right directory
if [ ! -f "app.yaml" ] || [ ! -f "simple_app.py" ]; then
  echo "Error: app.yaml or simple_app.py not found in current directory."
  echo "Make sure you're in the correct directory with the backend code."
  exit 1
fi

# Make sure the script is executable
chmod +x deploy.sh

# Install dependencies
echo "==== Installing requirements ===="
pip install -r requirements.txt

# Create .gcloudignore if needed
if [ ! -f .gcloudignore ]; then
  echo "==== Creating .gcloudignore file ===="
  cat > .gcloudignore << EOL
# .gcloudignore file
.git
.gitignore
archived/
google-cloud-sdk/
deployment-venv/
venv/
__pycache__/
*.pyc
*.pyo
.DS_Store
EOL
  echo ".gcloudignore created successfully."
fi

# Verify project is set correctly
echo "==== Verifying Google Cloud project ===="
PROJECT_ID=$(gcloud config get-value project)
echo "Current project ID: $PROJECT_ID"

if [ "$PROJECT_ID" != "clean-code-app-1744825963" ]; then
  echo "Setting project to clean-code-app-1744825963..."
  gcloud config set project clean-code-app-1744825963
fi

# Enable necessary APIs
echo "==== Enabling necessary APIs ===="
gcloud services enable appengine.googleapis.com secretmanager.googleapis.com

# Deploy to App Engine
echo "==== Deploying to App Engine ===="
gcloud app deploy app.yaml --quiet

echo "==== Deployment complete ===="
echo "Visit https://clean-code-app-1744825963.uc.r.appspot.com to see the app."
echo "Check app logs with: gcloud app logs tail"