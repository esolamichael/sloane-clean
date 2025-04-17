#!/bin/bash
echo "Running Netlify build script with enhanced checks"

echo "Checking environment..."
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

echo "Checking for Google Maps API key..."
if [ -z "$REACT_APP_GOOGLE_MAPS_API_KEY" ]; then
  echo "WARNING: REACT_APP_GOOGLE_MAPS_API_KEY is not set in the environment."
  echo "Google Maps features will rely on the Netlify function to get the API key."
  echo "Continuing with build..."
else
  echo "✅ REACT_APP_GOOGLE_MAPS_API_KEY is properly set in the environment."
fi

echo "Installing dependencies..."
npm install --legacy-peer-deps

echo "Building the application..."
CI=false SKIP_PREFLIGHT_CHECK=true npm run build

echo "Build completed."

# Verify the build
if [ -d "build" ]; then
  echo "✅ Build directory exists"
  ls -la build
  
  if [ -f "build/index.html" ]; then
    echo "✅ index.html exists in build directory"
    
    # Check for JavaScript files
    JS_FILES=$(find build -name "*.js" | wc -l)
    if [ "$JS_FILES" -gt 0 ]; then
      echo "✅ Found $JS_FILES JavaScript files in build"
    else
      echo "❌ No JavaScript files found in build directory"
      exit 1
    fi
    
    # Check for CSS files
    CSS_FILES=$(find build -name "*.css" | wc -l)
    if [ "$CSS_FILES" -gt 0 ]; then
      echo "✅ Found $CSS_FILES CSS files in build"
    else
      echo "❌ No CSS files found in build directory"
      exit 1
    fi
    
    echo "Build verification successful."
  else
    echo "❌ index.html missing from build directory"
    exit 1
  fi
else
  echo "❌ Build directory missing"
  exit 1
fi