// src/components/common/NetworkStatusIndicator.jsx
import React from 'react';
import { Snackbar, Alert } from '@mui/material';
import useNetworkStatus from '../../utils/useNetworkStatus';

const NetworkStatusIndicator = () => {
  const isOnline = useNetworkStatus();
  
  return (
    <Snackbar
      open={!isOnline}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
    >
      <Alert 
        severity="error" 
        sx={{ width: '100%' }}
      >
        You are currently offline. Some features may not work correctly.
      </Alert>
    </Snackbar>
  );
};

export default NetworkStatusIndicator;
