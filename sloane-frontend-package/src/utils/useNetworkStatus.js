// src/utils/useNetworkStatus.js
import { useState, useEffect } from 'react';

// Hook to detect network connectivity changes
const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    // Event handler for online status
    const handleOnline = () => {
      setIsOnline(true);
    };

    // Event handler for offline status
    const handleOffline = () => {
      setIsOnline(false);
    };

    // Add event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Clean up event listeners
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
};

export default useNetworkStatus;
