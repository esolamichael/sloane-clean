# Google Maps API Setup Guide

This comprehensive guide will help you set up and troubleshoot Google Maps integration for the business search autocomplete functionality in the Sloane AI Phone application.

## API Key Configuration

The application is designed to retrieve the Google Maps API key securely from environment variables. **Never hardcode API keys directly in the code.**

### Production Environment Setup (Netlify)

1. In your Netlify dashboard, go to "Site settings" > "Environment variables"
2. Add a new variable with one of the following names (in order of preference):
   - `GOOGLE_MAPS_API_KEY` (recommended)
   - `GOOGLE_PLACES_API_KEY`
   - `MAPS_API_KEY`
3. Set the value to your actual Google Maps API key
4. Click "Save" to store the environment variable
5. Trigger a new deployment for changes to take effect:
   - Go to "Deploys" and click "Trigger deploy" > "Deploy site"

### Local Development Setup

1. Create a `.env` file in the project root directory if it doesn't exist already
2. Add your Google Maps API key:
   ```
   REACT_APP_GOOGLE_MAPS_API_KEY=your-actual-api-key-here
   ```
3. Restart your development server: `npm start`

## Creating a Google Maps API Key

If you need to create a new API key:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing project
3. Navigate to "APIs & Services" > "Library"
4. Enable the following APIs:
   - Maps JavaScript API
   - Places API
   - Geocoding API
5. Go to "APIs & Services" > "Credentials"
6. Click "Create Credentials" > "API Key"
7. In the API key details, add appropriate restrictions:
   - For HTTP referrers, add your domains (including Netlify domain and any custom domains)
   - For localhost testing, add `localhost/*` and `127.0.0.1/*`
8. Save the API key

## API Key Security Best Practices

- **NEVER** commit API keys to version control
- Always use environment variables
- Apply appropriate API key restrictions in Google Cloud Console:
  - Restrict by HTTP referrers (allowed websites)
  - Set usage quotas to prevent unexpected charges
  - Monitor usage in Google Cloud Console

## Loading Mechanism

The application uses a secure, robust approach to load the Google Maps API:

1. The Netlify function `getGoogleApiKey.js` retrieves the API key from environment variables
2. The application fetches this key securely at runtime
3. The Google Maps JavaScript API is loaded dynamically with the retrieved key
4. Multiple fallback mechanisms ensure reliability

## Troubleshooting Common Issues

### InvalidKeyMapError

This error indicates an issue with your Google Maps API key:

1. Verify the API key is correctly set in your environment variables
2. Check the API key permissions in Google Cloud Console:
   - Ensure the Maps JavaScript API and Places API are enabled
   - Verify your domain is included in the HTTP referrer restrictions
   - Check that the billing account is active and valid

### API Not Loading

If the Google Maps API doesn't load:

1. **Check browser console** for specific error messages
2. Verify your Netlify function logs for any API key retrieval issues:
   - Go to Netlify dashboard > Functions > Check logs for `getGoogleApiKey`
3. Test your API key directly:
   - Try loading `https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=console.log` in a browser
4. Check for network issues or ad blockers that might prevent loading

### Fallback Mode

The application includes a fallback mode with sample business data if the Google Maps API cannot be loaded. When in fallback mode:

- A warning banner is displayed to the user
- A predefined set of sample businesses will be available
- All core functionality remains available with mock data

## Testing Your Setup

To verify your Google Maps integration is working properly:

1. Open the application in your browser
2. Navigate to the business onboarding flow
3. The Google Places autocomplete should appear without errors
4. Type a business name and see autocomplete suggestions
5. Select a business to confirm it loads the details correctly

## Monitoring and Maintenance

- Regularly check your Google Cloud Console for:
  - API usage and quotas
  - Billing status
  - Any error reports
- Review the Netlify function logs periodically for any issues with the API key retrieval

---

For additional help:

- [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
- [Netlify Environment Variables Documentation](https://docs.netlify.com/configure-builds/environment-variables/)
- Contact your administrator for specific project settings