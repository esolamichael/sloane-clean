import api from './index';

// Mock data has been removed.
// We now always use real API data for business information.

// Function to fetch the Google Maps API key from the Netlify function
const getGoogleApiKey = async () => {
  try {
    console.log('[Maps API] Fetching Google API key from Netlify function...');
    
    // Add cache-busting parameter to avoid cached responses
    const timestamp = new Date().getTime();
    const url = `/.netlify/functions/getGoogleApiKey?_t=${timestamp}`;
    
    // First try Netlify function endpoint with proper fetch options
    try {
      console.log(`[Maps API] Making request to: ${url}`);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10-second timeout
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        },
        cache: 'no-store',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      console.log(`[Maps API] Response status: ${response.status}`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.apiKey) {
          console.log('[Maps API] API key successfully received from Netlify function');
          return data.apiKey;
        } else {
          console.warn('[Maps API] API key missing from Netlify function response:', data);
          throw new Error('API key missing from Netlify function response');
        }
      } else {
        console.error('[Maps API] Failed to fetch API key, status:', response.status);
        const text = await response.text();
        console.error('[Maps API] Response:', text);
        throw new Error(`Failed to fetch API key: ${response.status} - ${text}`);
      }
    } catch (netlifyError) {
      // Check if this is an abort error (timeout)
      if (netlifyError.name === 'AbortError') {
        console.error('[Maps API] Request to Netlify function timed out');
        throw new Error('Request to Netlify function timed out');
      }
      
      console.error('[Maps API] Error accessing Netlify function:', netlifyError);
      
      // Try fallback options but bubble up the original error if all fallbacks fail
      const originalError = netlifyError;
      
      // Try direct environment variable (for local development)
      console.log('[Maps API] Trying to access API key from environment directly (for local development)');
      if (process.env && process.env.REACT_APP_GOOGLE_MAPS_API_KEY) {
        console.log('[Maps API] Found API key in REACT_APP_GOOGLE_MAPS_API_KEY environment variable');
        return process.env.REACT_APP_GOOGLE_MAPS_API_KEY;
      }
      
      // All fallbacks failed, throw the original error
      throw originalError;
    }
  } catch (error) {
    console.error('[Maps API] Error fetching Google API key:', error);
    throw error;
  }
};

// Simple test function to directly test GBP scraper
export const testGBPScraper = async (businessName) => {
  console.log('🔍 DIRECT TEST: Testing GBP scraper with business name:', businessName);
  
  try {
    // Get API URL
    let apiBaseUrl = '';
    if (process.env.NODE_ENV === 'development') {
      apiBaseUrl = 'http://localhost:8000/api';
    } else {
      apiBaseUrl = '/api';
    }
    
    console.log('🔍 DIRECT TEST: Using API base URL:', apiBaseUrl);
    
    // First test the health endpoint
    try {
      console.log('🔍 DIRECT TEST: Testing API health endpoint...');
      const healthResponse = await fetch(`${apiBaseUrl}/health`);
      console.log('🔍 DIRECT TEST: Health endpoint status:', healthResponse.status);
      console.log('🔍 DIRECT TEST: Health endpoint ok:', healthResponse.ok);
      const healthData = await healthResponse.json();
      console.log('🔍 DIRECT TEST: Health endpoint response:', healthData);
    } catch (healthError) {
      console.error('🔍 DIRECT TEST: Error checking API health:', healthError);
    }
    
    // Now test the GBP test endpoint
    try {
      console.log('🔍 DIRECT TEST: Testing GBP test endpoint...');
      const testResponse = await fetch(`${apiBaseUrl}/gbp/test`);
      console.log('🔍 DIRECT TEST: GBP test endpoint status:', testResponse.status);
      console.log('🔍 DIRECT TEST: GBP test endpoint ok:', testResponse.ok);
      const testData = await testResponse.json();
      console.log('🔍 DIRECT TEST: GBP test endpoint response:', testData);
    } catch (testError) {
      console.error('🔍 DIRECT TEST: Error checking GBP test endpoint:', testError);
    }
    
    // Finally, try the actual scrape-gbp endpoint
    console.log('🔍 DIRECT TEST: Testing real GBP scraper endpoint...');
    const endpoint = `${apiBaseUrl}/business/scrape-gbp`;
    console.log('🔍 DIRECT TEST: Endpoint URL:', endpoint);
    
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Business-ID': 'test_business_id',
        'Accept': 'application/json',
        'Cache-Control': 'no-cache'
      },
      body: JSON.stringify({ 
        business_name: businessName,
        location: "San Francisco", 
        _t: new Date().getTime()
      })
    });
    
    console.log('🔍 DIRECT TEST: GBP scraper status:', response.status);
    console.log('🔍 DIRECT TEST: GBP scraper ok:', response.ok);
    
    const data = await response.json();
    console.log('🔍 DIRECT TEST: GBP scraper response:', data);
    
    return {
      success: true,
      result: data
    };
  } catch (error) {
    console.error('🔍 DIRECT TEST: Error testing GBP scraper:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

const businessApi = {
  // Get Google API key
  getGoogleApiKey,
  
  // Test function
  testGBPScraper,
  
  // Real API methods now used instead of mock implementations
  
  // Search business on Google Business Profile - replaced with real API call
  searchGoogleBusiness: async (query) => {
    try {
      console.log(`Searching for business: ${query} using real API call`);
      // Get API URL
      let apiBaseUrl = '';
      if (process.env.NODE_ENV === 'development') {
        apiBaseUrl = 'http://localhost:8000/api';
      } else {
        apiBaseUrl = '/api';
      }
      
      const response = await fetch(`${apiBaseUrl}/business/search?q=${encodeURIComponent(query)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Error searching for business: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error searching for business:", error);
      throw error;
    }
  },
  
  // Get business details - replaced with real API call
  getGoogleBusinessDetails: async (businessId) => {
    try {
      console.log(`Getting details for business ID: ${businessId} using real API call`);
      // Get API URL
      let apiBaseUrl = '';
      if (process.env.NODE_ENV === 'development') {
        apiBaseUrl = 'http://localhost:8000/api';
      } else {
        apiBaseUrl = '/api';
      }
      
      const response = await fetch(`${apiBaseUrl}/business/details/${businessId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Error getting business details: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error getting business details:", error);
      throw error;
    }
  },
  
  // Scrape website data
  scrapeWebsite: async (url) => {
    try {
      console.log(`Attempting to scrape website: ${url}`);
      
      // Validate URL
      if (!url) {
        throw new Error('No URL provided');
      }
      
      // Ensure URL has http or https prefix
      let normalizedUrl = url;
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        normalizedUrl = 'https://' + url;
        console.log(`Normalized URL to: ${normalizedUrl}`);
      }
      
      // Add business_id header for authorization
      const headers = {
        'X-Business-ID': 'test_business_id'
      };
      
      // Get API URL from the environment or use default
      let apiBaseUrl = '';
      
      // If running locally, use the local API
      if (process.env.NODE_ENV === 'development') {
        apiBaseUrl = 'http://localhost:8000/api';
        console.log('Using local API for scraping:', apiBaseUrl);
      } else {
        // For production, use relative URL or App Engine URL depending on deployment
        apiBaseUrl = '/api'; // Use relative URL for Netlify -> App Engine proxy
        console.log('Using production API for scraping:', apiBaseUrl);
      }
      
      const endpoint = `${apiBaseUrl}/business/scrape-website`;
      console.log(`Making request to: ${endpoint}`);
      
      // Add timestamp to avoid caching
      const timestamp = new Date().getTime();
      
      // Use direct fetch with proper CORS settings and timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30-second timeout
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers,
          'Accept': 'application/json',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        },
        body: JSON.stringify({ 
          url: normalizedUrl,
          _t: timestamp // Add timestamp to avoid caching
        }),
        mode: 'cors',
        credentials: 'omit',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      console.log('Received response:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries([...response.headers])
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`HTTP error! Status: ${response.status}, Body: ${errorText}`);
        throw new Error(`HTTP error! Status: ${response.status}, Details: ${errorText || 'No additional error details'}`);
      }
      
      const data = await response.json();
      console.log('Scrape website response:', data);
      return data;
    } catch (error) {
      console.error("Error scraping website:", error);
      if (error.name === 'AbortError') {
        throw new Error('Request timed out. The server took too long to respond.');
      }
      throw error;
    }
  },
  
  // Scrape Google Business Profile data
  scrapeGBP: async (businessName, location = null) => {
    try {
      console.log(`Attempting to scrape GBP for business: ${businessName}`);
      
      // Validate business name
      if (!businessName) {
        throw new Error('No business name provided');
      }
      
      // Add business_id header for authorization
      const headers = {
        'X-Business-ID': 'test_business_id'
      };
      
      // Get API URL from the environment or use default
      let apiBaseUrl = '';
      
      // If running locally, use the local API
      if (process.env.NODE_ENV === 'development') {
        apiBaseUrl = 'http://localhost:8000/api';
        console.log('Using local API for scraping GBP:', apiBaseUrl);
      } else {
        // For production, use relative URL or App Engine URL depending on deployment
        apiBaseUrl = '/api'; // Use relative URL for Netlify -> App Engine proxy
        console.log('Using production API for scraping GBP:', apiBaseUrl);
      }
      
      const endpoint = `${apiBaseUrl}/business/scrape-gbp`;
      console.log(`Making request to: ${endpoint}`);
      
      // Add timestamp to avoid caching
      const timestamp = new Date().getTime();
      
      // Use direct fetch with proper CORS settings and timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30-second timeout
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers,
          'Accept': 'application/json',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        },
        body: JSON.stringify({ 
          business_name: businessName, 
          location,
          _t: timestamp // Add timestamp to avoid caching
        }),
        mode: 'cors',
        credentials: 'omit',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      console.log('Received response:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries([...response.headers])
      });
      
      // Always parse the response even if not ok
      const data = await response.json();
      console.log('Scrape GBP response data:', data);
      
      // Handle 200 response with error field
      if (data && data.success === false) {
        console.error('API returned error message:', data.error);
        throw new Error(data.error || 'API error occurred when scraping GBP data');
      }
      
      // Handle HTTP errors
      if (!response.ok) {
        console.error(`HTTP error! Status: ${response.status}, Response:`, data);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return data;
    } catch (error) {
      console.error("Error scraping Google Business Profile:", error);
      if (error.name === 'AbortError') {
        throw new Error('Request timed out. The server took too long to respond.');
      }
      throw error;
    }
  },
  
  // Get business profile
  getBusinessProfile: async () => {
    try {
      const response = await api.get('/business/profile');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update business profile
  updateBusinessProfile: async (profileData) => {
    try {
      const response = await api.put('/business/profile', profileData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get business hours
  getBusinessHours: async () => {
    try {
      const response = await api.get('/business/hours');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update business hours
  updateBusinessHours: async (hoursData) => {
    try {
      const response = await api.put('/business/hours', hoursData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get business services
  getBusinessServices: async () => {
    try {
      const response = await api.get('/business/services');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update business services
  updateBusinessServices: async (servicesData) => {
    try {
      const response = await api.put('/business/services', servicesData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get business FAQs
  getBusinessFAQs: async () => {
    try {
      const response = await api.get('/business/faqs');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update business FAQs
  updateBusinessFAQs: async (faqsData) => {
    try {
      const response = await api.put('/business/faqs', faqsData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default businessApi;