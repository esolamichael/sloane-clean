# Sloane AI Phone Answering Service - Deployment Instructions

This document provides step-by-step instructions for deploying the Sloane frontend application to Netlify using your GitHub repository.

## Prerequisites

- Node.js (v14 or higher) and npm installed on your computer
- Git installed on your computer
- GitHub account with access to the repository at https://github.com/esolamichael/ai-phone-service
- Netlify account (free tier is sufficient)

## Local Setup and Testing

Before deploying, it's recommended to test the application locally:

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/esolamichael/ai-phone-service.git
   cd ai-phone-service
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the root directory with the following content:
   ```
   REACT_APP_API_URL=https://fluted-mercury-455419-n0.uc.r.appspot.com/api
   ```

4. Start the development server:
   ```bash
   npm start
   ```

5. Verify the application is working correctly at http://localhost:3000

## Preparing for Deployment

1. Build the production version of the application:
   ```bash
   npm run build
   ```

2. Test the production build locally (optional):
   ```bash
   npx serve -s build
   ```

## Deployment to Netlify

### Option 1: Deploy via Netlify CLI (Terminal)

1. Install the Netlify CLI globally:
   ```bash
   npm install -g netlify-cli
   ```

2. Login to Netlify:
   ```bash
   netlify login
   ```

3. Initialize a new Netlify site:
   ```bash
   netlify init
   ```
   - Select "Create & configure a new site"
   - Choose your team
   - Provide a site name (or leave blank for a random name)

4. Configure build settings when prompted:
   - Build command: `npm run build`
   - Directory to deploy: `build`
   - Functions directory: Leave blank and press Enter

5. Deploy the site:
   ```bash
   netlify deploy --prod
   ```

6. Once deployment is complete, Netlify will provide a URL for your live site.

### Option 2: Deploy via GitHub Integration (Recommended)

1. Push your code to the GitHub repository:
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. Log in to your Netlify account at https://app.netlify.com/

3. Click "New site from Git"

4. Select "GitHub" as your Git provider

5. Authorize Netlify to access your GitHub account if prompted

6. Select the repository: `esolamichael/ai-phone-service`

7. Configure build settings:
   - Branch to deploy: `main`
   - Build command: `npm run build`
   - Publish directory: `build`

8. Click "Show advanced" and add the environment variable:
   - Key: `REACT_APP_API_URL`
   - Value: `https://fluted-mercury-455419-n0.uc.r.appspot.com/api`

9. Click "Deploy site"

10. Netlify will build and deploy your site. Once complete, you'll be provided with a URL for your live site.

## Custom Domain Setup (Optional)

If you want to use a custom domain for your Sloane application:

1. In the Netlify dashboard, go to your site settings

2. Click on "Domain management" → "Add custom domain"

3. Enter your domain name and follow the instructions to configure DNS settings

## Continuous Deployment

With the GitHub integration, Netlify will automatically rebuild and redeploy your site whenever you push changes to the main branch of your repository.

## Troubleshooting

If you encounter issues during deployment:

1. Check the build logs in Netlify for any errors

2. Verify that all environment variables are correctly set

3. Ensure the API endpoint is accessible from the deployed application

4. For routing issues, make sure you have a `_redirects` file in the public directory with:
   ```
   /*    /index.html   200
   ```

## Support

If you need further assistance with deployment, please contact the development team or refer to the [Netlify documentation](https://docs.netlify.com/).
