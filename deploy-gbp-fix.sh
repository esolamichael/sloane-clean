#!/bin/bash
set -e

echo "----------------------------------------------------"
echo "Deploying updated application with GBP scraper fix"
echo "----------------------------------------------------"

# 1. Ensure Secret Manager is enabled
echo "Ensuring Secret Manager API is enabled for the project..."
gcloud services enable secretmanager.googleapis.com

# 2. Add IAM permissions for App Engine to access Secret Manager
echo "Granting Secret Manager access to App Engine service account..."
PROJECT_ID="clean-code-app-1744825963"
APP_ENGINE_SA="clean-code-app-1744825963@appspot.gserviceaccount.com"
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${APP_ENGINE_SA}" \
    --role="roles/secretmanager.secretAccessor"

# 3. Set project configuration
echo "Setting the project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# 4. Verify temp files are cleaned up
rm -rf /tmp/deploy_cache || true
mkdir -p /tmp/deploy_cache

# 5. Copy all necessary files to temp directory
echo "Preparing deployment files..."
cp -r app /tmp/deploy_cache/
cp main.py /tmp/deploy_cache/
cp requirements.txt /tmp/deploy_cache/

# 6. Create a clean app.yaml file
echo "Creating app.yaml file..."
cat > /tmp/deploy_cache/app.yaml << 'EOF'
runtime: python39
entrypoint: gunicorn -b :$PORT main:app
env_variables:
  API_HOST: "https://clean-code-app-1744825963.uc.r.appspot.com"
  MONGODB_NAME: "sloane_ai_service" 
  TWILIO_ACCOUNT_SID: "AC8cc057f196bec4492fd4a6e8da90aa8a"
  TWILIO_PHONE_NUMBER: "+14245295093"
  USE_SECRET_MANAGER: "true"
  GOOGLE_CLOUD_PROJECT: "clean-code-app-1744825963"
instance_class: F2
automatic_scaling:
  min_instances: 1
  max_instances: 3
  min_idle_instances: 1
  target_cpu_utilization: 0.65
  target_throughput_utilization: 0.65
  max_concurrent_requests: 50
EOF

echo "app.yaml file created successfully"

# 7. Run the deployment
echo "Deploying application to App Engine..."
cd /tmp/deploy_cache
gcloud app deploy app.yaml --version=fixed-gbp-scraper-v1 --quiet

echo "----------------------------------------------------"
echo "Deployment complete!"
echo "App URL: https://clean-code-app-1744825963.uc.r.appspot.com"
echo "----------------------------------------------------"