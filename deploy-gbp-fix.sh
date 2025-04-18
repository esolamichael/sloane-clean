#!/bin/bash
set -e

echo "----------------------------------------------------"
echo "Deploying updated application with GBP scraper fix v2"
echo "----------------------------------------------------"

# Set project ID
PROJECT_ID="clean-code-app-1744825963"
APP_ENGINE_SA="clean-code-app-1744825963@appspot.gserviceaccount.com"

# Set environment variables
export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
export USE_SECRET_MANAGER="true"

# 1. Ensure Secret Manager is enabled
echo "Ensuring Secret Manager API is enabled for the project..."
gcloud services enable secretmanager.googleapis.com

# 2. Add IAM permissions for App Engine to access Secret Manager
echo "Granting Secret Manager access to App Engine service account..."
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

# 6. Create a clean app.yaml file with enhanced environment variables
echo "Creating app.yaml file..."
cat > /tmp/deploy_cache/app.yaml << 'EOF'
runtime: python310
env: flex
entrypoint: gunicorn -b :$PORT main:app

env_variables:
  API_HOST: "https://clean-code-app-1744825963.uc.r.appspot.com"
  MONGODB_NAME: "sloane_ai_service"
  USE_SECRET_MANAGER: "true"
  GOOGLE_CLOUD_PROJECT: "clean-code-app-1744825963"
  TWILIO_ACCOUNT_SID: "AC8cc057f196bec4492fd4a6e8da90aa8a"
  TWILIO_PHONE_NUMBER: "+14245295093"
  DEBUG: "true"
instance_class: F2
automatic_scaling:
  min_num_instances: 1
  max_num_instances: 3
  cool_down_period_sec: 180
  cpu_utilization:
    target_utilization: 0.65
inbound_services:
- warmup
EOF

echo "app.yaml file created successfully"

# 7. Create logging.yaml file for detailed logging
echo "Creating logging.yaml file..."
cat > /tmp/deploy_cache/logging.yaml << 'EOF'
version: 1
formatters:
  standard:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: standard
    stream: ext://sys.stdout
loggers:
  '':
    level: INFO
    handlers: [console]
    propagate: no
  app.business.scrapers:
    level: DEBUG
    handlers: [console]
    propagate: no
  main:
    level: DEBUG
    handlers: [console]
    propagate: no
EOF

# 8. Verify Google Maps API key exists in Secret Manager
echo "Verifying Google Maps API key in Secret Manager..."
SECRET_EXISTS=$(gcloud secrets describe google-maps-api-key --project=${PROJECT_ID} 2>/dev/null || echo "not-exists")

if [[ "$SECRET_EXISTS" == *"not-exists"* ]]; then
  echo "ERROR: google-maps-api-key does not exist in Secret Manager."
  echo "Please create it with: gcloud secrets create google-maps-api-key --replication-policy="automatic""
  echo "Then add the value with: echo -n 'your-api-key' | gcloud secrets versions add google-maps-api-key --data-file=-"
  exit 1
else
  echo "Google Maps API key found in Secret Manager."
fi

# 9. Run the deployment with no-promote to allow testing
echo "Deploying application to App Engine..."
cd /tmp/deploy_cache
gcloud app deploy app.yaml --version=fixed-gbp-scraper-v2 --no-promote --quiet

# 10. Test the GBP scraper with the new version
echo "Testing GBP scraper endpoint..."
NEW_VERSION_URL="https://fixed-gbp-scraper-v2-dot-clean-code-app-1744825963.uc.r.appspot.com"
echo "Sending test request to: ${NEW_VERSION_URL}/api/health"

# Use curl to check if the new version is working
HEALTH_CHECK=$(curl -s "${NEW_VERSION_URL}/api/health" || echo "Connection failed")

if [[ "$HEALTH_CHECK" == *"healthy"* ]]; then
  echo "Health check passed! New version is responding correctly."
  
  # Now promote the new version to receive all traffic
  echo "Promoting new version to receive all traffic..."
  gcloud app services set-traffic default --splits fixed-gbp-scraper-v2=1 --quiet
  
  echo "----------------------------------------------------"
  echo "Deployment complete and new version promoted!"
  echo "App URL: https://clean-code-app-1744825963.uc.r.appspot.com"
  echo "----------------------------------------------------"
else
  echo "WARNING: Health check failed with response: ${HEALTH_CHECK}"
  echo "New version has been deployed but not promoted."
  echo "You can manually test and promote it at: ${NEW_VERSION_URL}"
  echo "To promote: gcloud app services set-traffic default --splits fixed-gbp-scraper-v2=1"
  echo "----------------------------------------------------"
fi