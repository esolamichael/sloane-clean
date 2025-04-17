# Netlify Deployment Guide

This project is configured to deploy to Netlify. Here are the key points about the deployment:

## Configuration Files

1. **netlify.toml** - The main configuration file that Netlify uses
   - Located at the project root
   - Specifies build commands, publish directory, and environment settings
   - **IMPORTANT**: Only this root netlify.toml file should be used

2. **Environment Variables**
   - `NODE_VERSION` - Set to Node.js 16
   - `NPM_CONFIG_LEGACY_PEER_DEPS` - Set to "true" to handle peer dependency issues
   - `CI` - Set to "false" to prevent build failures on warnings

## Required Environment Variables

Make sure to set the following environment variables in your Netlify dashboard:

- `GOOGLE_MAPS_API_KEY` or `REACT_APP_GOOGLE_MAPS_API_KEY` - Your Google Maps API key (REACT_APP_GOOGLE_MAPS_API_KEY is prioritized if present)

## Updated Build Settings

- Base directory: `sloane-frontend-package`
- Build command: `cd sloane-frontend-package && NODE_OPTIONS=--max-old-space-size=4096 npm install --legacy-peer-deps && CI=false npm run build`
- Publish directory: `sloane-frontend-package/build`

## API Key Access

The Google Maps API key is accessed via:
- A Netlify serverless function: `/sloane-frontend-package/netlify/functions/getGoogleApiKey.js`
- Environment variables set in the Netlify dashboard (not hardcoded in code)

## Avoided Recursion Issues

To prevent infinite recursion during builds:
- Root `package.json` no longer contains a build script
- The sloane-frontend-package/netlify.toml file is fully deprecated and should be ignored
- The build command in the root netlify.toml explicitly changes directory first

## Troubleshooting

If you encounter build issues:

1. Check the build logs in the Netlify dashboard
2. Verify that all required environment variables are set
3. Make sure your Google API key has the necessary permissions and APIs enabled
4. Check for any conflicting build configuration files

## Manual Deployment

If automatic deployments aren't working, you can deploy manually:

1. Run `cd sloane-frontend-package && npm install --legacy-peer-deps && npm run build` locally
2. Drag and drop the `sloane-frontend-package/build` folder to Netlify's manual deploy section