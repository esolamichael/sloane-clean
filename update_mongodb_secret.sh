#!/bin/bash

# This script updates the MongoDB connection string in Secret Manager
# Replace the placeholder with your actual MongoDB connection string
# Format: mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority

# DO NOT COMMIT THIS FILE AFTER ADDING REAL CREDENTIALS

# Check if MONGODB_URI is set
if [ -z "$MONGODB_URI" ]; then
    echo "Error: MONGODB_URI environment variable is not set"
    exit 1
fi

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud is not installed"
    exit 1
fi

# Update the secret
echo "Updating mongodb-connection secret..."
echo -n "$MONGODB_URI" | gcloud secrets versions add mongodb-connection --data-file=- --project=clean-code-app-1744825963

if [ $? -eq 0 ]; then
    echo "Successfully updated MongoDB secret"
else
    echo "Failed to update MongoDB secret"
    exit 1
fi

echo "Secret updated successfully. Remember to remove your connection string from this file!"