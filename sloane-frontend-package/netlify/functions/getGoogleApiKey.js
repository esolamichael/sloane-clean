exports.handler = async function(event, context) {
  console.log('📞 API Key function called');
  console.log('Request details:', {
    path: event.path,
    httpMethod: event.httpMethod,
    headers: event.headers
  });
  
  // Set CORS headers to allow all origins in development
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS'
  };
  
  // Handle preflight OPTIONS request
  if (event.httpMethod === "OPTIONS") {
    console.log('⚪ Handling OPTIONS request');
    return {
      statusCode: 204,
      headers: corsHeaders,
      body: ''
    };
  }
  
  // Only allow GET requests
  if (event.httpMethod !== "GET") {
    console.log('⛔ Rejecting non-GET request:', event.httpMethod);
    return { 
      statusCode: 405, 
      headers: corsHeaders,
      body: JSON.stringify({ error: "Method Not Allowed" }) 
    };
  }

  console.log('✅ GET request confirmed');

  // List all environment variables (names only, not values) for debugging
  const envVarNames = Object.keys(process.env);
  console.log('Environment variables available:', envVarNames);
  
  // Get the API key from environment variables
  // Make sure to set this in your Netlify environment variables
  const apiKey = process.env.GOOGLE_PLACES_API_KEY;
  
  console.log('API Key exists:', !!apiKey);
  
  if (!apiKey) {
    console.log('⛔ No API key found in environment variables');
    console.log('Looking for GOOGLE_PLACES_API_KEY variable');
    
    return { 
      statusCode: 500, 
      headers: {
        "Content-Type": "application/json",
        ...corsHeaders
      },
      body: JSON.stringify({ 
        error: "API key is not configured in environment variables",
        availableEnvVars: envVarNames.join(', ')
      }) 
    };
  }

  // Mask key for logging
  const maskedKey = apiKey.substring(0, 4) + '...' + apiKey.substring(apiKey.length - 4);
  console.log(`✅ Returning API key: ${maskedKey}`);

  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders
    },
    body: JSON.stringify({ apiKey })
  };
};