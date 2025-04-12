// src/api/index.js
import axios from 'axios';
import authApi from './auth';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'https://fluted-mercury-455419-n0.uc.r.appspot.com/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Flag to prevent multiple refresh token requests
let isRefreshing = false;
// Queue of failed requests to retry after token refresh
let failedQueue = [];

// Process failed queue
const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

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
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 Unauthorized errors (token expired or invalid)
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      // If token refresh already in progress, queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(token => {
            originalRequest.headers['Authorization'] = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch(err => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;
      
      try {
        // Don't use authApi here to avoid circular dependency
        // Direct axios call to refresh token
        const refreshToken = localStorage.getItem('refreshToken');
        
        if (!refreshToken) {
          // If no refresh token, clear auth and redirect to login
          localStorage.removeItem('token');
          localStorage.removeItem('refreshToken');
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
          return Promise.reject(error);
        }

        const response = await axios.post(
          `${api.defaults.baseURL}/auth/refresh-token`,
          { refreshToken },
          { headers: { 'Content-Type': 'application/json' } }
        );

        if (response.data.token) {
          localStorage.setItem('token', response.data.token);
          if (response.data.refreshToken) {
            localStorage.setItem('refreshToken', response.data.refreshToken);
          }
          
          api.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
          originalRequest.headers['Authorization'] = `Bearer ${response.data.token}`;
          
          // Process any queued requests
          processQueue(null, response.data.token);
          
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Token refresh failed, clear auth and redirect to login
        processQueue(refreshError, null);
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');

        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      } finally {
        isRefreshing = false;
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
