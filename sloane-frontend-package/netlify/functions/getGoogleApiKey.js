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
    // You must set GOOGLE_MAPS_API_KEY in Netlify dashboard
    const apiKey = process.env.GOOGLE_MAPS_API_KEY;
    
    // Check if we have the API key
    if (!apiKey) {
      return { 
        statusCode: 500, 
        headers,
        body: JSON.stringify({ 
          error: "API key not configured in environment variables",
          message: "Please set GOOGLE_MAPS_API_KEY in Netlify dashboard"
        })
      };
    }

    // Return the API key successfully
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ apiKey })
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: "Server error",
        message: error.message
      })
    };
  }
};