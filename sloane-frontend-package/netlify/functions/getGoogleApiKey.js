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
    // Get API key from environment variable
    // REACT_APP_GOOGLE_MAPS_API_KEY is already configured in Netlify
    const apiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;
    
    if (!apiKey) {
      console.error('REACT_APP_GOOGLE_MAPS_API_KEY environment variable is not set');
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ 
          error: "API key not configured",
          message: "REACT_APP_GOOGLE_MAPS_API_KEY environment variable is not set in Netlify",
          timestamp: new Date().toISOString()
        })
      };
    }
    
    console.log('Successfully retrieved Google Maps API key from environment variable');
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
        timestamp: new Date().toISOString()
      })
    };
  }
};