// Simple Netlify function to return a Google Maps API key
exports.handler = async function(event, context) {
  // Set CORS headers to allow all origins
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Content-Type': 'application/json'
  };
  
  // Handle preflight OPTIONS request
  if (event.httpMethod === "OPTIONS") {
    return {
      statusCode: 204,
      headers,
      body: ''
    };
  }

  try {
    // No API keys in code - only environment variables
    // Search for API key in multiple possible environment variable names
    const possibleEnvVars = [
      'GOOGLE_MAPS_API_KEY',
      'REACT_APP_GOOGLE_MAPS_API_KEY',
      'GOOGLE_PLACES_API_KEY',
      'MAPS_API_KEY',
      'PLACES_API_KEY',
      'GOOGLE_API_KEY'
    ];
    
    let apiKey = null;
    
    // Check each possible environment variable
    for (const envVar of possibleEnvVars) {
      if (process.env[envVar]) {
        apiKey = process.env[envVar];
        console.log(`Found API key in ${envVar}`);
        break;
      }
    }
    
    // Log all available environment variables for troubleshooting (without their values)
    const envVars = Object.keys(process.env)
      .filter(key => key.includes('GOOGLE') || key.includes('API') || key.includes('KEY') || key.includes('MAP'))
      .map(key => ({ key, exists: !!process.env[key] }));
    
    console.log('Environment variables available:', JSON.stringify(envVars));
    
    // Check if we have the API key
    if (!apiKey) {
      console.error('No Google Maps API key found in environment variables');
      return { 
        statusCode: 500, 
        headers,
        body: JSON.stringify({ 
          error: "API key not configured in environment variables",
          message: "Please set GOOGLE_MAPS_API_KEY in Netlify dashboard",
          availableVars: envVars.map(v => v.key),
          timestamp: new Date().toISOString()
        })
      };
    }

    // Return the API key successfully
    console.log('Successfully retrieved Google Maps API key');
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ 
        apiKey,
        timestamp: new Date().toISOString() 
      })
    };
  } catch (error) {
    console.error('Error in getGoogleApiKey function:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: "Server error",
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString()
      })
    };
  }
};