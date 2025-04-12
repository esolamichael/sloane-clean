import React from 'react';
import { Box, Typography, Paper, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import SuperSimpleDashboard from '../../components/dashboard/SuperSimpleDashboard';

// This is a standalone page that doesn't require modifications to your existing structure
const StandaloneAnalyticsPage = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4">Call Analytics Dashboard</Typography>
          <Button 
            component={Link} 
            to="/dashboard" 
            variant="outlined"
          >
            Back to Dashboard
          </Button>
        </Box>
        <Typography variant="body1" color="text.secondary" paragraph>
          View and analyze your call data with interactive charts and metrics.
        </Typography>
      </Paper>
      
      <SuperSimpleDashboard />
    </Box>
  );
};

export default StandaloneAnalyticsPage;

