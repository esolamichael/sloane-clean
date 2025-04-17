#!/bin/bash

# deploy.sh - Helper script for deploying to Google App Engine

echo "Starting deployment process..."

# Make sure we have the right permissions
chmod +x deploy.sh

# Install dependencies for deployment
echo "Installing requirements..."
pip install -r requirements.txt

# Update .gcloudignore if it doesn't exist
if [ ! -f .gcloudignore ]; then
  echo "Creating .gcloudignore file..."
  echo -e "# .gcloudignore file\n.git\n.gitignore\narchived/\ngoogle-cloud-sdk/\ndeployment-venv/\nvenv/\n__pycache__/\n*.pyc\n*.pyo\n.DS_Store" > .gcloudignore
fi

# Deploy to App Engine
echo "Deploying to App Engine..."
gcloud app deploy app.yaml --quiet

echo "Deployment complete. Visit https://clean-code-app-1744825963.uc.r.appspot.com to see the app."
echo "Check app logs with: gcloud app logs tail"