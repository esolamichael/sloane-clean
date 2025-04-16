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
  
  // IMPORTANT SECURITY NOTE: For actual production use, you should never hardcode API keys
  // in a function. However, since this is a temporary fix for a debugging issue,
  // we're providing the API key directly in the function code.
  // In a production environment, you should always use environment variables.
  
  // This is the current API key that was added to Netlify's environment variables
  const googleMapsApiKey = "AIzaSyCzeU0fgbvLUM6N39RgxuK9amo-rL_raZk";
  
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