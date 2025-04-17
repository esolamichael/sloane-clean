#\!/bin/bash

# Deploy script for the Clean Code App

echo "Starting deployment to Google App Engine..."

# Set project ID
PROJECT_ID="clean-code-app-1744825963"

# Make sure gcloud is using the correct project
echo "Setting project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Deploy the application
echo "Deploying application to App Engine..."
gcloud app deploy app.yaml --quiet

echo "Deployment complete\! Check logs for any issues:"
echo "gcloud app logs tail -s default"

echo "Open the application in your browser:"
echo "gcloud app browse"
