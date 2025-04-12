#!/bin/bash

# This script ensures all CallToActionSection.jsx files point to the onboarding page
# and rebuilds the application

echo "Fixing all Call to Action buttons to point to onboarding..."

# Find all CallToActionSection.jsx files and update them
find . -name "CallToActionSection.jsx" -type f -exec sed -i '' 's|to="/signup"|to="/onboarding"|g' {} \;

echo "Building the application..."
npm run build

echo "Build completed. The 'Get Started for Free' button should now redirect to /onboarding"