#!/bin/bash

echo "Current directory: $(pwd)"
echo "Directory listing:"
ls -la

echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

echo "Checking for Google Maps API key environment variable..."
if [ -z "$REACT_APP_GOOGLE_MAPS_API_KEY" ]; then
  echo "ERROR: REACT_APP_GOOGLE_MAPS_API_KEY is not set. This must be configured in Netlify environment variables."
  exit 1
else
  echo "✅ REACT_APP_GOOGLE_MAPS_API_KEY is properly set in Netlify environment."
fi

echo "Installing dependencies..."
npm install --legacy-peer-deps

echo "Fixing all Call to Action buttons..."
find . -name "CallToActionSection.jsx" -type f -exec sed -i.bak 's|to="/signup"|to="/onboarding"|g' {} \;

echo "Building application..."
CI=false npm run build || CI=false npm run-script build

echo "Build completed. Output directory:"
ls -la build