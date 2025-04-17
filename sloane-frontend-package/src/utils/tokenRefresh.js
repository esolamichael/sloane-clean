// src/utils/tokenRefresh.js
import { useEffect, useState } from 'react';

// This is a custom hook to handle token refresh
export const useTokenRefresh = (currentUser, refreshTokenFunction) => {
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
          await refreshTokenFunction();
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
  }, [currentUser, refreshTokenFunction]);

  return { isRefreshing };
};

export default useTokenRefresh;
