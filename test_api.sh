#!/bin/bash
# Script to test the API endpoints

# Set a business ID for testing
BUSINESS_ID="test-business-123"

echo -e "\n==== Testing Health Check ===="
curl -s "http://localhost:8000/api/health" | jq .

echo -e "\n==== Testing Scrape Website ===="
curl -s -X POST "http://localhost:8000/api/business/scrape-website" \
  -H "Content-Type: application/json" \
  -H "X-Business-ID: $BUSINESS_ID" \
  -d '{"url": "https://example.com"}' | jq .

echo -e "\n==== Testing Training Data ===="
curl -s "http://localhost:8000/api/business/training-data?business_id=$BUSINESS_ID" | jq .

echo -e "\n==== Testing Call Simulation ===="
curl -s -X POST "http://localhost:8000/api/business/call" \
  -H "Content-Type: application/json" \
  -H "X-Business-ID: $BUSINESS_ID" \
  -d '{"caller_number": "+15551234567", "twilio_sid": "CA123456789"}' | jq .

echo -e "\n==== Testing Analytics Dashboard ===="
curl -s "http://localhost:8000/api/business/analytics/dashboard?business_id=$BUSINESS_ID&days=30" | jq .