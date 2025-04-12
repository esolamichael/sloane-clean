import React, { useEffect, useState } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import { useAuth } from '../../contexts/AuthContext';

// This is a custom hook to handle token refresh
export const useTokenRefresh = () => {
  const { currentUser, refreshToken } = useAuth();
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    if (!currentUser) return;

    // Function to check token expiration and refresh if needed
    const checkTokenExpiration = async () => {
      try {
        // Get token expiration from JWT
        const token = currentUser.token;
        if (!token) return;

        // Decode the JWT to get expiration time
        const tokenData = JSON.parse(atob(token.split('.')[1]));
        const expirationTime = tokenData.exp * 1000; // Convert to milliseconds
        const currentTime = Date.now();
        
        // If token is about to expire in the next 5 minutes, refresh it
        const fiveMinutesInMs = 5 * 60 * 1000;
        if (expirationTime - currentTime < fiveMinutesInMs) {
          setIsRefreshing(true);
          await refreshToken();
          setIsRefreshing(false);
        }
      } catch (error) {
        console.error('Error checking token expiration:', error);
        setIsRefreshing(false);
      }
    };

    // Check token expiration immediately
    checkTokenExpiration();

    // Set up interval to check token expiration every minute
    const intervalId = setInterval(checkTokenExpiration, 60000);

    // Clean up interval on unmount
    return () => clearInterval(intervalId);
  }, [currentUser, refreshToken]);

  return { isRefreshing };
};

// Update the AuthContext.jsx file to include the refreshToken function
export const AuthContextUpdated = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Add refreshToken function to the context
  const refreshToken = async () => {
    try {
      // Call the refresh token API endpoint
      const response = await fetch('https://fluted-mercury-455419-n0.uc.r.appspot.com/api/auth/refresh-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refreshToken: localStorage.getItem('refreshToken'),
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }

      const data = await response.json();
      
      // Update the tokens in localStorage
      localStorage.setItem('token', data.token);
      localStorage.setItem('refreshToken', data.refreshToken);
      
      // Update the current user with the new token
      setCurrentUser(prevUser => ({
        ...prevUser,
        token: data.token,
      }));

      return data.token;
    } catch (error) {
      console.error('Error refreshing token:', error);
      // If refresh fails, log the user out
      logout();
      throw error;
    }
  };

  // Rest of the AuthContext implementation...
  // ...

  return (
    <AuthContext.Provider value={{ 
      currentUser, 
      loading, 
      login, 
      signup, 
      logout, 
      resetPassword,
      refreshToken // Add the refreshToken function to the context
    }}>
      {children}
    </AuthContext.Provider>
  );
};
