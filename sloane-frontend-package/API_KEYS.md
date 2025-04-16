# API Key Management

## Security Guidelines

API keys and other sensitive credentials should never be committed to the Git repository. Here are the proper ways to handle them:

### Local Development

1. Copy the `.env.example` file to `.env` (which is git-ignored)
2. Add your actual API keys to the `.env` file
3. The application will read keys from this file during development

### Production Deployment (Netlify)

Set API keys in the Netlify dashboard:
1. Go to Site settings > Build & deploy > Environment variables
2. Add your API keys as environment variables
3. These will be securely injected during build time

### Current API Keys

For security reasons, we use Netlify Functions to fetch API keys:
- Google Maps API key is retrieved from the `/.netlify/functions/getGoogleApiKey` endpoint
- This endpoint securely retrieves the key from Netlify environment variables

## API Key Configuration

The following API keys are needed:

| Service      | Environment Variable             | Purpose                            |
|--------------|----------------------------------|-----------------------------------|
| Google Maps  | REACT_APP_GOOGLE_MAPS_API_KEY    | Business location autocomplete    |
| Google Places| (same as above)                  | Business information search       |

## Updating API Keys

1. When you need to update an API key, update it in the Netlify dashboard
2. Deploy the site to apply the changes
3. Never commit actual API keys to the repository

### API Key Rotating Schedule

As a best practice, API keys should be rotated periodically:
- Review and rotate API keys every 3 months
- Immediately rotate keys if there's any suspicion of a security breach