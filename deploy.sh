#\!/bin/bash

# Deploy script for the Clean Code App

echo "Starting deployment to Google App Engine..."

# Set project ID
PROJECT_ID="clean-code-app-1744825963"

# Make sure gcloud is using the correct project
echo "Setting project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Copy essential files to a temporary directory
DEPLOY_TMP="/tmp/deploy_essentials"
rm -rf ${DEPLOY_TMP} || true
mkdir -p ${DEPLOY_TMP}
mkdir -p ${DEPLOY_TMP}/app/api/routes ${DEPLOY_TMP}/app/business ${DEPLOY_TMP}/app/database ${DEPLOY_TMP}/app/utils ${DEPLOY_TMP}/app/config ${DEPLOY_TMP}/app/repositories

# Copy only the essential files
cp app.yaml ${DEPLOY_TMP}/
cp main.py ${DEPLOY_TMP}/
cp requirements.txt ${DEPLOY_TMP}/
cp -r app/business/scrapers.py ${DEPLOY_TMP}/app/business/
cp -r app/business/analytics.py ${DEPLOY_TMP}/app/business/  # Added analytics.py
cp -r app/api/routes/business_data.py ${DEPLOY_TMP}/app/api/routes/
cp -r app/database/mongo.py ${DEPLOY_TMP}/app/database/
cp -r app/database/mongo_db.py ${DEPLOY_TMP}/app/database/
cp -r app/utils/secrets.py ${DEPLOY_TMP}/app/utils/
cp -r app/config/secrets.py ${DEPLOY_TMP}/app/config/

# Copy repositories modules - needed for GBP scraper
cp -r app/repositories/*.py ${DEPLOY_TMP}/app/repositories/

# Create required __init__.py files
touch ${DEPLOY_TMP}/app/__init__.py
touch ${DEPLOY_TMP}/app/api/__init__.py
touch ${DEPLOY_TMP}/app/api/routes/__init__.py
touch ${DEPLOY_TMP}/app/business/__init__.py
touch ${DEPLOY_TMP}/app/database/__init__.py
touch ${DEPLOY_TMP}/app/utils/__init__.py
touch ${DEPLOY_TMP}/app/config/__init__.py
touch ${DEPLOY_TMP}/app/repositories/__init__.py

# Deploy the application
echo "Deploying application to App Engine..."
cd ${DEPLOY_TMP}
gcloud app deploy app.yaml --quiet

echo "Deployment complete\! Check logs for any issues:"
echo "gcloud app logs tail -s default"

echo "Open the application in your browser:"
echo "gcloud app browse"
