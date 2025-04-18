#!/bin/bash

echo "Running post-build script to fix CTA button redirects..."

# Navigate to the build directory
cd build

# Find the main JS file
MAIN_JS=$(find static/js -name "main.*.js" | head -n 1)

if [ -z "$MAIN_JS" ]; then
  echo "Error: Could not find main JS file"
  exit 1
fi

echo "Found main JS file: $MAIN_JS"

# Backup the original file
cp "$MAIN_JS" "$MAIN_JS.bak"

# Create a fixed version using perl (more reliable than sed for this case)
perl -i -pe 's#to:"/signup"#to:"/onboarding"#g' "$MAIN_JS"
perl -i -pe 's#to:\\\\\"/signup\\\\"#to:\\\\"/onboarding\\\\"#g' "$MAIN_JS"

# Check if replacements were made
grep -n "signup" "$MAIN_JS" | grep -i "router" || echo "No signup links found - replacement successful!"

echo "Post-build script completed"