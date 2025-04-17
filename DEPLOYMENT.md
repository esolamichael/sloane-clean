# Deployment Instructions

## Backend (Google App Engine)

The backend is deployed to Google App Engine. Follow these instructions:

### Simplified Deployment Using Google Cloud Shell (Recommended)

1. Open Google Cloud Console: https://console.cloud.google.com/
2. Make sure you're in the "Clean Code App" project
3. Click the Cloud Shell icon (>_) in the top right corner
4. In Cloud Shell, clone your repository:
   ```
   git clone https://github.com/esolamichael/sloane-clean.git
   cd sloane-clean
   ```
5. Run the deployment script:
   ```
   bash deploy.sh
   ```
6. The application will be deployed to: https://clean-code-app-1744825963.uc.r.appspot.com

### Manual Deployment Steps

If you prefer to deploy manually:

1. Open Google Cloud Console and launch Cloud Shell
2. Clone your repository:
   ```
   git clone https://github.com/esolamichael/sloane-clean.git
   cd sloane-clean
   ```
3. Make sure the right APIs are enabled:
   ```
   gcloud services enable appengine.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   ```
4. Deploy to App Engine:
   ```
   gcloud app deploy app.yaml --quiet
   ```
5. Check the logs to verify deployment:
   ```
   gcloud app logs tail
   ```

### Option 2: Service Account Authentication (Better for CI/CD)

1. Install and initialize Google Cloud SDK as in Option 1 steps 1-5

2. Download a service account key from Google Cloud Console
   - Go to IAM & Admin > Service Accounts
   - Create or select an existing service account with App Engine Admin role
   - Create a new JSON key and download it
   - Secure this key file - don't commit it to version control!

3. Store your service account key in Secret Manager:
   ```
   # Create the secret
   gcloud secrets create app-service-account-key --replication-policy="automatic"
   
   # Add the key file
   gcloud secrets versions add app-service-account-key --data-file=PATH_TO_YOUR_KEY_FILE.json
   
   # Also store other sensitive values
   gcloud secrets create mongodb-connection --replication-policy="automatic"
   echo -n "YOUR_MONGODB_CONNECTION_STRING" | gcloud secrets versions add mongodb-connection --data-file=-
   
   gcloud secrets create twilio-auth-token --replication-policy="automatic"
   echo -n "YOUR_TWILIO_AUTH_TOKEN" | gcloud secrets versions add twilio-auth-token --data-file=-
   ```
   
4. Authenticate with the service account:
   ```
   gcloud auth activate-service-account --key-file=PATH_TO_YOUR_KEY_FILE.json
   ```

4. Set the project and deploy:
   ```
   gcloud config set project PROJECT_ID
   gcloud app deploy app.yaml --quiet --no-cache
   ```

5. The application will be deployed to: https://PROJECT_ID.uc.r.appspot.com

### Required Secrets in Secret Manager

The following secrets **MUST** be set up in Google Cloud Secret Manager:

- `MONGODB_URL`: The MongoDB connection string
- `GOOGLE_MAPS_API_KEY`: API key for Google Maps Places API
- `TWILIO_AUTH_TOKEN`: Auth token for Twilio integration

#### Setting Up Secrets in Secret Manager

1. Go to Security → Secret Manager in the Google Cloud Console
2. Click "Create Secret"
3. Enter the secret name exactly as shown above
4. Add the secret value
5. Click "Create Secret"

#### Giving App Engine Access to Secrets

After creating the secrets, you must give the App Engine service account permission to access them:

1. Go to each secret in Secret Manager
2. Click "Add Member"
3. Add the App Engine service account: `[PROJECT_ID]@appspot.gserviceaccount.com`
4. Assign the role "Secret Manager Secret Accessor"

This step is **CRITICAL**. Without these permissions, the application will fail to access the secrets.

### Important CORS Notes

The backend has been configured with proper CORS settings to allow connections from any origin. The key settings are:

1. CORS headers in the Flask application
2. Special handling for OPTIONS preflight requests

If you need to debug CORS issues:
- Check browser dev tools Network tab for CORS errors
- Review the server logs with: `gcloud app logs tail`

## Frontend (Netlify)

The frontend is automatically deployed when changes are pushed to the GitHub repository. The deployment is configured with Netlify's continuous deployment.

1. Changes to the `main` branch trigger a new build on Netlify
2. Netlify builds the React application using the build command in `netlify.toml`
3. The application is deployed to: https://sloane-ai-phone.netlify.app

### Important Configuration Notes

The frontend is configured to connect to the backend using direct API calls with proper CORS settings. There are several key configuration files:

1. `netlify.toml` - Main Netlify configuration
2. `public/_redirects` - URL redirect rules for Netlify

These rules enable proper routing for:
- API calls to the backend
- Frontend routing for React single-page application

## API Integration

The frontend communicates with the backend through several API endpoints:

- `/api/business/scrape-website` - Scrape website data during onboarding
- `/api/business/scrape-gbp` - Scrape Google Business Profile data during onboarding

These endpoints require the `X-Business-ID` header for authentication. They allow CORS from all origins to simplify development and deployment.