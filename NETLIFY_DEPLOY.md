# Netlify Deployment Guide

This project is configured to deploy to Netlify. Here are the key points about the deployment:

## Configuration Files

1. **netlify.toml** - The main configuration file that Netlify uses
   - Located at the project root
   - Specifies build commands, publish directory, and environment settings

2. **Environment Variables**
   - `NODE_VERSION` - Set to Node.js 16
   - `NPM_CONFIG_LEGACY_PEER_DEPS` - Set to "true" to handle peer dependency issues
   - `CI` - Set to "false" to prevent build failures on warnings

## Required Environment Variables

Make sure to set the following environment variables in your Netlify dashboard:

- `GOOGLE_PLACES_API_KEY` - Your Google Maps API key for the Places API

## Build Settings

- Base directory: `sloane-frontend-package`
- Build command: `npm install --legacy-peer-deps && npm run build`
- Publish directory: `build`

## Troubleshooting

If you encounter build issues:

1. Check the build logs in the Netlify dashboard
2. Verify that all required environment variables are set
3. Make sure your Google API key has the necessary permissions and APIs enabled

## Manual Deployment

If automatic deployments aren't working, you can deploy manually:

1. Run `npm run build` locally
2. Drag and drop the `build` folder to Netlify's manual deploy section