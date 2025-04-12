# Google Maps API Setup Guide

This guide will help you set up and troubleshoot Google Maps integration for the business search autocomplete functionality.

## API Key Configuration Options

There are two ways to provide your Google Maps API key:

### Option 1: Environment Variable (Recommended for local development)

1. Edit the `.env` file in the project root directory
2. Replace `your_google_maps_api_key_here` with your actual API key:
   ```
   REACT_APP_GOOGLE_MAPS_API_KEY=your-actual-api-key-here
   ```
3. Restart your development server: `npm start`

### Option 2: Netlify Environment Variable (For production)

1. In your Netlify dashboard, go to "Site settings" > "Environment variables"
2. Add a new variable named `GOOGLE_PLACES_API_KEY` with your API key as the value
3. Deploy your site again for changes to take effect

## Manual Testing Option (HTML Script Tag)

For quick testing without rebuilding:

1. Open `public/index.html` in a code editor
2. Find the commented script tag near line 45
3. Uncomment it and replace `YOUR_API_KEY_HERE` with your actual API key
4. Save the file and refresh your browser

```html
<script async defer src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY_HERE&libraries=places&callback=initGoogleMapsAPI"></script>
```

## Troubleshooting

If you're experiencing issues with the Google Maps API:

1. **Check your browser console** for any error messages
2. Verify that your API key has the following APIs enabled in the Google Cloud Console:
   - Places API
   - Maps JavaScript API
   - Geocoding API
3. Make sure your API key has appropriate restrictions (HTTP referrers) that include your domain
4. If using localhost, ensure you've allowed it in your API key restrictions
5. Clear your browser cache and reload
6. For Netlify deploys, check the function logs for any errors

## Fallback Behavior

The application has a built-in fallback mechanism with sample business data that will be used if:

- The Google Maps API can't be loaded
- Your API key is missing or invalid
- There are network issues or API quota limits reached

You'll see a warning banner when the fallback mechanism is active.

---

For further help, check the [Google Maps Platform documentation](https://developers.google.com/maps/documentation) or contact your administrator.