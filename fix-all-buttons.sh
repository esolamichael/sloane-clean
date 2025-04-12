#!/bin/bash

# This script will fix all instances of CallToActionSection.jsx to point to /onboarding
# and will also build a completely new version of the application

echo "Starting comprehensive fix for all CTA buttons..."

# Step 1: Fix source files
echo "Fixing all source CallToActionSection.jsx files..."
find /Users/Mike/Documents/ai-phone-service-codebase-v2 -name "CallToActionSection.jsx" -type f -exec bash -c 'echo "Fixing $1"; sed -i.bak "s|to=\"/signup\"|to=\"/onboarding\"|g" "$1"' _ {} \;

# Step 2: Add a new Route component for handling /signup redirects
echo "Creating a redirect component..."
mkdir -p /Users/Mike/Documents/ai-phone-service-codebase-v2/sloane-frontend-package/src/components/redirects
cat > /Users/Mike/Documents/ai-phone-service-codebase-v2/sloane-frontend-package/src/components/redirects/SignupRedirect.jsx << 'EOF'
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const SignupRedirect = () => {
  const navigate = useNavigate();
  
  useEffect(() => {
    console.log('Redirecting from /signup to /onboarding');
    navigate('/onboarding', { replace: true });
  }, [navigate]);
  
  return (
    <div>Redirecting to onboarding...</div>
  );
};

export default SignupRedirect;
EOF

# Step 3: Modify the App.jsx file to use the redirect component
echo "Updating App.jsx to include the redirect component..."
TEMP_FILE=$(mktemp)
APP_FILE="/Users/Mike/Documents/ai-phone-service-codebase-v2/sloane-frontend-package/src/App.jsx"

# Read the file and replace the SignupPage with our redirect component
cat "$APP_FILE" | sed -e '/import SignupPage/a\
import SignupRedirect from '\''./components/redirects/SignupRedirect'\'';
' -e 's|<Route path="signup" element={<SignupPage />} />|<Route path="signup" element={<SignupRedirect />} />|g' > "$TEMP_FILE"

# Replace the original file with our modified version
cp "$TEMP_FILE" "$APP_FILE"
rm "$TEMP_FILE"

# Step 4: Update the public/_redirects file to ensure it's properly formatted
echo "Updating Netlify redirects file..."
cat > /Users/Mike/Documents/ai-phone-service-codebase-v2/sloane-frontend-package/public/_redirects << EOF
/signup    /onboarding    301!
/*    /index.html   200
EOF

# Step 5: Build the application
echo "Building the application..."
cd /Users/Mike/Documents/ai-phone-service-codebase-v2/sloane-frontend-package
npm run build

echo "Comprehensive fix complete. All instances of the CTA button should now redirect to /onboarding."
echo "Please commit and push these changes to deploy to Netlify."