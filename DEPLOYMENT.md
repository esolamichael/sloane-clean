# Deployment Instructions

## Backend (Google App Engine)

The backend is deployed to Google App Engine. Follow these instructions:

### Option 1: Interactive Deployment (Recommended for Local Development)

1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
   - If you already have the SDK in your project directory, initialize it with:
   ```
   ./google-cloud-sdk/install.sh --usage-reporting=false --path-update=true
   ```
   - Then restart your terminal/shell for the PATH changes to take effect

2. Install the App Engine Python component:
   ```
   gcloud components install app-engine-python
   ```

3. Login to your Google Cloud account:
   ```
   gcloud auth login
   ```
   - This will open a browser window for authentication
   - If browser doesn't open, follow the URL displayed in your terminal

4. Create a new project (if needed) or select an existing project:
   ```
   # Create a new project (optional)
   gcloud projects create PROJECT_ID --name="PROJECT_NAME"
   
   # Set the project
   gcloud config set project PROJECT_ID
   ```

5. Enable required APIs:
   ```
   gcloud services enable appengine.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable storage.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   ```

6. Create an App Engine application in your preferred region:
   ```
   gcloud app create --region=us-central
   ```

7. Update the app.yaml file with your new project endpoint URL:
   ```
   # Update the API_HOST environment variable in app.yaml
   API_HOST: "https://PROJECT_ID.uc.r.appspot.com"
   ```

8. Create a .gcloudignore file to exclude unnecessary files:
   ```
   echo -e "# .gcloudignore file\n.git\n.gitignore\narchived/\ngoogle-cloud-sdk/\ndeployment-venv/\nvenv/\n__pycache__/\n*.pyc\n*.pyo\n.DS_Store" > .gcloudignore
   ```

9. Deploy the application:
   ```
   gcloud app deploy app.yaml --quiet --no-cache
   ```

10. The application will be deployed to: https://PROJECT_ID.uc.r.appspot.com

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

### Important CORS Notes

The backend has been configured with proper CORS settings to allow connections from any origin. The key settings are:

1. CORS middleware in FastAPI
2. Additional CORS headers in a custom middleware
3. Special handling for OPTIONS preflight requests

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