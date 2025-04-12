import React from 'react';
import { createContext, useContext, useState, useEffect } from 'react';
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
      const userData = await authApi.getCurrentUser();
      setCurrentUser(userData);
    } catch (err) {
      console.error('Failed to fetch current user:', err);
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  // Login function
  const login = async (email, password) => {
    setError(null);
    try {
      const response = await authApi.login(email, password);
      localStorage.setItem('token', response.token);
      setCurrentUser(response.user);
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
      const response = await authApi.signup(userData);
      localStorage.setItem('token', response.token);
      setCurrentUser(response.user);
      return response.user;
    } catch (err) {
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
    resetPassword
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
