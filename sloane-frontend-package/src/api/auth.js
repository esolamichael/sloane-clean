// src/api/auth.js
import api from './index';

const authApi = {
  // Login user
  login: async (email, password) => {
    // Check if we should use mock response (if real API is down)
    const useMockResponse = true; // Set to false when real API is working
    
    if (useMockResponse) {
      console.log('Using mock login response');
      // Return a mock successful response
      return new Promise((resolve) => {
        // Simulate network delay
        setTimeout(() => {
          const mockResponse = {
            user: {
              id: 'mock-user-id',
              firstName: 'User',
              lastName: 'Name',
              email: email,
              businessName: 'Business Name'
            },
            token: 'mock-jwt-token-' + Math.random().toString(36).substring(2),
            refreshToken: 'mock-refresh-token-' + Math.random().toString(36).substring(2)
          };
          console.log('Mock login response:', mockResponse);
          resolve(mockResponse);
        }, 800); // simulate network delay
      });
    }
    
    // Original implementation for when the API is working
    try {
      const response = await api.post('/auth/login', { email, password });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Register new user
  signup: async (userData) => {
    console.log('Signup API call with data:', userData);
    
    // Check if we should use mock response (if real API is down)
    const useMockResponse = true; // Set to false if you want to use the real API
    
    if (useMockResponse) {
      console.log('Using mock signup response');
      // Return a mock successful response
      return new Promise((resolve) => {
        // Simulate network delay
        setTimeout(() => {
          const mockResponse = {
            user: {
              id: 'mock-user-id',
              firstName: userData.firstName,
              lastName: userData.lastName,
              email: userData.email,
              businessName: userData.businessName
            },
            token: 'mock-jwt-token-' + Math.random().toString(36).substring(2),
            refreshToken: 'mock-refresh-token-' + Math.random().toString(36).substring(2)
          };
          console.log('Mock signup response:', mockResponse);
          resolve(mockResponse);
        }, 800); // simulate network delay
      });
    }
    
    // Original implementation for when the API is working
    try {
      const response = await api.post('/auth/register', userData);
      console.log('Signup API response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Signup API error:', error);
      throw error;
    }
  },

  // Logout user
  logout: async () => {
    try {
      await api.post('/auth/logout');
      return true;
    } catch (error) {
      throw error;
    }
  },

  // Get current user data
  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Send password reset email
  forgotPassword: async (email) => {
    try {
      const response = await api.post('/auth/forgot-password', { email });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Reset password with token
  resetPassword: async (token, password) => {
    try {
      const response = await api.post('/auth/reset-password', { token, password });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Refresh token
  refreshToken: async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      const response = await api.post('/auth/refresh-token', { refreshToken });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Verify email with token
  verifyEmail: async (token) => {
    try {
      const response = await api.post('/auth/verify-email', { token });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default authApi;
