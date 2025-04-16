exports.handler = async function(event, context) {
  // Set CORS headers to allow all origins
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS'
  };
  
  // Handle preflight OPTIONS request
  if (event.httpMethod === "OPTIONS") {
    return {
      statusCode: 204,
      headers: corsHeaders,
      body: ''
    };
  }
  
  // Get API key from environment variables only
  // NEVER hardcode API keys in code
  const googleMapsApiKey = process.env.GOOGLE_MAPS_API_KEY;
  
  // Check if we have the API key
  if (!googleMapsApiKey) {
    return { 
      statusCode: 500, 
      headers: {
        "Content-Type": "application/json",
        ...corsHeaders
      },
      body: JSON.stringify({ 
        error: "API key is not available"
      }) 
    };
  }

  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders
    },
    body: JSON.stringify({ apiKey: googleMapsApiKey })
  };
};
};