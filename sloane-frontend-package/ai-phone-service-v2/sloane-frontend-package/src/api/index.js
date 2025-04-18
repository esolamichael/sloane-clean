import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'https://fluted-mercury-455419-n0.uc.r.appspot.com/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized errors (token expired or invalid)
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login if not already there
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    
    // Format error message
    const errorMessage = 
      error.response?.data?.message || 
      error.message || 
      'An unexpected error occurred';
    
    return Promise.reject(new Error(errorMessage));
  }
);

export default api;
