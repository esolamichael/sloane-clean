#!/bin/bash
echo "Running minimal Netlify build script"
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

echo "Installing dependencies..."
npm install --legacy-peer-deps

echo "Building the application..."
CI=false npm run build

echo "Build completed."