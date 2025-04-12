#!/bin/bash
echo "Current directory: $(pwd)"
echo "Directory listing:"
ls -la

echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

echo "Installing dependencies..."
npm install --legacy-peer-deps

echo "Fixing all Call to Action buttons..."
find . -name "CallToActionSection.jsx" -type f -exec sed -i.bak 's|to="/signup"|to="/onboarding"|g' {} \;

echo "Building application..."
CI=false npm run build

echo "Build completed. Output directory:"
ls -la build