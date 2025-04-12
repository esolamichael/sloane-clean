// src/contexts/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import authApi from '../api/auth';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is already logged in
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  // Fetch current user data
  const fetchCurrentUser = async () => {
    try {
      setLoading(true);
      const userData = await authApi.getCurrentUser();
      setCurrentUser({
        ...userData,
        token: localStorage.getItem('token')
      });
    } catch (err) {
      console.error('Failed to fetch current user:', err);
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
    } finally {
      setLoading(false);
    }
  };

  // Refresh token function
  const refreshToken = useCallback(async () => {
    try {
      // Call the refresh token API endpoint
      const response = await authApi.refreshToken();
      
      // Update the tokens in localStorage
      localStorage.setItem('token', response.token);
      if (response.refreshToken) {
        localStorage.setItem('refreshToken', response.refreshToken);
      }
      
      // Update the current user with the new token
      setCurrentUser(prevUser => ({
        ...prevUser,
        token: response.token,
      }));

      return response.token;
    } catch (error) {
      console.error('Error refreshing token:', error);
      // If refresh fails, log the user out
      logout();
      throw error;
    }
  }, []);

  // Login function
  const login = async (email, password) => {
    setError(null);
    try {
      const response = await authApi.login(email, password);
      localStorage.setItem('token', response.token);
      if (response.refreshToken) {
        localStorage.setItem('refreshToken', response.refreshToken);
      }
      setCurrentUser({
        ...response.user,
        token: response.token
      });
      return response.user;
    } catch (err) {
      setError(err.message || 'Failed to login');
      throw err;
    }
  };

  // Signup function
  const signup = async (userData) => {
    setError(null);
    try {
      console.log('AuthContext: Starting signup process');
      const response = await authApi.signup(userData);
      console.log('AuthContext: Received signup response', response);
      
      // Store tokens in localStorage
      if (response.token) {
        localStorage.setItem('token', response.token);
      } else {
        console.error('AuthContext: No token in response');
      }
      
      if (response.refreshToken) {
        localStorage.setItem('refreshToken', response.refreshToken);
      }
      
      // Update the current user state
      if (response.user) {
        setCurrentUser({
          ...response.user,
          token: response.token
        });
        console.log('AuthContext: User state updated');
      } else {
        console.error('AuthContext: No user data in response');
      }
      
      return response.user;
    } catch (err) {
      console.error('AuthContext: Signup error', err);
      setError(err.message || 'Failed to sign up');
      throw err;
    }
  };

  // Logout function
  const logout = async () => {
    setError(null);
    try {
      await authApi.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      setCurrentUser(null);
    }
  };

  // Forgot password function
  const forgotPassword = async (email) => {
    setError(null);
    try {
      return await authApi.forgotPassword(email);
    } catch (err) {
      setError(err.message || 'Failed to send password reset email');
      throw err;
    }
  };

  // Reset password function
  const resetPassword = async (token, password) => {
    setError(null);
    try {
      return await authApi.resetPassword(token, password);
    } catch (err) {
      setError(err.message || 'Failed to reset password');
      throw err;
    }
  };

  const value = {
    currentUser,
    loading,
    error,
    login,
    signup,
    logout,
    forgotPassword,
    resetPassword,
    refreshToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export { AuthContext };
