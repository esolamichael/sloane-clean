# Deployment Instructions

## Backend (Google App Engine)

The backend is deployed to Google App Engine. To deploy:

1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
2. Login to your Google Cloud account:
   ```
   gcloud auth login
   ```
3. Set the correct project:
   ```
   gcloud config set project fluted-mercury-455419
   ```
4. Deploy the application:
   ```
   gcloud app deploy app.yaml --quiet
   ```
5. The application will be deployed to: https://fluted-mercury-455419-n0.uc.r.appspot.com

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